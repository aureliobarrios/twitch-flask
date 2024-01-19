from flask import Flask, request, session, render_template

from processing import calculate_mode
import pandas as pd

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "lkmaslkdsldsamdlsdmasldsmkdd"

data = pd.read_csv("data/twitch_data.csv")

known_streamers = list(data['lower_handles']) + list(data['lower_channel'])

@app.route("/", methods=["GET", "POST"])
def mode_page():
    items = "<datalist id='items'>"

    for streamer in known_streamers:
        include_option = "<option value='" + streamer + "'>"
        items += include_option

    items += "</datalist>"

    if "inputs" not in session:
        session["inputs"] = []

    errors = ""
    if request.method == "POST":
        try:
            if request.form["streamer"].lower() not in known_streamers:
                raise ValueError()
            elif request.form["streamer"].lower() in session["inputs"]:
                raise AttributeError()
            else:
                session["inputs"].append(request.form["streamer"].lower())
                session.modified = True
        except ValueError:
            errors += "<p style='text-align: center; color: red;  font-size: 20px;'>Could not find {!r} twitter handle or twitch channel name, please try again.</p>\n".format(request.form["streamer"])
        except AttributeError:
            errors += "<p style='text-align: center; color: red;  font-size: 20px;'>The {!r} handle has already been given, please give new handle.</p>\n".format(request.form["streamer"])

        if request.form["action"] == "Recommend Streamers":
            result = calculate_mode(session["inputs"])
            session["inputs"].clear()
            session.modified = True
            return render_template("recommended.html", result=result)

    if len(session["inputs"]) == 0:
        numbers_so_far = ""
    else:
        numbers_so_far = "<p style='text-align: center; font-size: 20px;'>Streamers you follow</p>"
        for number in session["inputs"]:
            numbers_so_far += "<p style='text-align: center; font-size: 20px;'>{}</p>".format(number)

    return '''
    <!DOCTYPE html>
    <html>

    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link href="https://fonts.googleapis.com/css?family=Quicksand:300,500" rel="stylesheet">

    </head>

    <body style="font-family: 'Quicksand', sans-serif; font-weight: 300;">
        <div class="recommendor" style="padding-top: 5%;">
            <h1 style="text-align: center; font-weight: 500">Twitch Streamer Recommendor</h1>
            {numbers_so_far}
            {errors}
            <form method="post" action="." style="text-align: center;">
                <p style="text-align: center; font-size: 20px;"><input id="search" list="items" oninput="filterList()" style="text-align: center; font-size: 18px;" size="40" class="main-input" name="streamer" /></p>
                <p style="text-align: center; font-size: 20px;">Enter streamers you already follow (Twitter or Twitch handle)</p>
                <p style="text-align: center; font-size: 20px;"><input style="font-size: 15px;" type="submit" name="action" value="Add another" /> <input style="font-size: 15px;" type="submit"
                        name="action" value="Recommend Streamers" /></p>
            </form>
            {items}    
        </div>
        <script src="static/search.js"></script>
    </body>

    </html>
    '''.format(numbers_so_far=numbers_so_far, errors=errors, items=items)