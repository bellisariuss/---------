from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import datetime
import pandas as pd
import os
import joblib

# Зареждаме моделите и енкодерите
model_length = joblib.load("rf_model_length.pkl")
model_type = joblib.load("rf_model_type.pkl")
label_encoders = joblib.load("rf_label_encoders.pkl")
print(label_encoders["стил"].classes_)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/resort/<resort>', methods=["GET", "POST"])
def show_resort(resort):
    image_map = {
        "pamporovo": "images/pamporovo.jpg",
        "borovets": "images/ec84d3e850.jpg",
        "bansko": "images/ski-map.jpg"
    }
    image = image_map.get(resort.lower(), "images/default.jpg")
    recommendation = None
    warning = None
    piste_color = "Зелена"

    if request.method == "POST" and "skill" in request.form:
        skill_map = {
            "beginner": "Начинаещ",
            "intermediate": "Средно ниво",
            "advanced": "Експерт",
            "expert": "Експерт",
            "Напреднал": "Експерт",
        }
        style_map = {
            "all-mountain": "all-mountain",
            "All mountain": "all-mountain",
            "all mountain": "all-mountain",
            "dynamic": "dynamic",
            "Dynamic": "dynamic",
            "speed": "speed",
            "Speed": "speed",
        }
        piste_color_map = {
            "green": "Зелена",
            "blue": "Синя",
            "red": "Червена",
            "black": "Черна"
        }

        raw_skill = request.form.get('skill')
        raw_style = request.form.get('style', 'all-mountain')
        raw_piste = request.form.get('piste_color')

        height = int(request.form.get('height', 170))
        weight = int(request.form.get('weight', 70))

        skill = skill_map.get(raw_skill)
        style = style_map.get(raw_style, "all-mountain")
        piste_color = piste_color_map.get(raw_piste, "Зелена")

        if skill == "advanced" and style == "dynamic" and piste_color == "Черна":
            style = "slalom"

        if skill is None:
            return f"Невалидно ниво: {raw_skill}", 400
        if style is None:
            return f"Невалиден стил: {raw_style}", 400

        if skill == "Начинаещ" and piste_color == "Черна":
            warning = "Черната писта не е подходяща за начинаещи. Моля, изберете зелена писта."
        else:
            entry = {
                "ниво": label_encoders["ниво"].transform([skill])[0],
                "ръст": height,
                "стил": label_encoders["стил"].transform([style])[0],
                "писта": label_encoders["писта"].transform([piste_color])[0]
            }

            X_input = pd.DataFrame([entry])
            predicted_length = model_length.predict(X_input)[0]
            predicted_type_code = model_type.predict(X_input)[0]
            predicted_type = label_encoders["тип ски"].inverse_transform([predicted_type_code])[0]

            if predicted_type == "slalom" and skill != "Експерт":
                warning = "Slalom ски са позволени само за експерти. Моля, изберете друг стил или подобрете уменията си."
                recommendation = None
                entry["стил"] = label_encoders["стил"].transform(["all-mountain"])[0]
                X_input = pd.DataFrame([entry])
                predicted_length = model_length.predict(X_input)[0]
                predicted_type_code = model_type.predict(X_input)[0]
                predicted_type = label_encoders["тип ски"].inverse_transform([predicted_type_code])[0]
                if predicted_type != "slalom":
                    recommendation = f"Препоръчителна дължина: {predicted_length} см, тип ски: {predicted_type}"
                    warning = "Slalom не е позволен за вашето ниво. Предлагаме All-Mountain."
            else:
                allowed_types = {
                    "Начинаещ": ["all-mountain"],
                    "Средно ниво": ["all-mountain", "slalom"],
                    "Експерт": ["all-mountain", "slalom", "piste"]
                }

                if predicted_type.lower() not in [t.lower() for t in allowed_types[skill]]:
                    warning = f"{predicted_type.capitalize()} ски са позволени само за по-високо ниво. Моля, изберете друг стил или подобрете уменията си."
                    recommendation = None
                else:
                    recommendation = f"Препоръчителна дължина: {predicted_length} см, тип ски: {predicted_type}"

            if recommendation:
                log_row = {
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "resort": resort,
                    "skill": skill,
                    "height": height,
                    "style": style,
                    "piste_color": piste_color,
                    "length": predicted_length,
                    "ski_type": predicted_type
                }
                log_file = 'logs.csv'
                if not os.path.exists(log_file):
                    pd.DataFrame([log_row]).to_csv(log_file, index=False)
                else:
                    pd.DataFrame([log_row]).to_csv(log_file, mode='a', header=False, index=False)

    return render_template(
        "resort_form.html",
        resort=resort.capitalize(),
        image=image,
        recommendation=recommendation,
        warning=warning,
        piste_color=piste_color,
        skill=skill if 'skill' in locals() else None,
        predicted_type=locals().get("predicted_type"),
        predicted_length=locals().get("predicted_length")
    )

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    email = request.form.get("email")
    stars = request.form.get("stars")
    length = request.form.get("length")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = request.remote_addr
    cookies = request.cookies.to_dict()

    row = {
        "timestamp": timestamp,
        "email": email,
        "length": length,
        "stars": stars,
        "ip": ip_address,
        "cookies": str(cookies)
    }

    file_exists = os.path.exists("feedback.csv")
    df = pd.DataFrame([row])
    df.to_csv("feedback.csv", mode='a', header=not file_exists, index=False)

    resp = make_response(redirect(url_for("index")))
    resp.set_cookie("feedback_given", "yes", max_age=60*60*24)
    return resp

if __name__ == '__main__':
    app.run(debug=True)
