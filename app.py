import os

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename

from config import app, db, login_manager
from models import User, Log
from forms import RegisterForm, LoginForm
from utils import allowed_file, read_and_save_log_in_db, time_validations, filter_logs, unpack_archive, prepare_file


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        flash("You are already logged in.")
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(password=form.password.data):
            login_user(user)
            flash("Logged in successfully.", "info")
            return redirect(url_for("index"))

        else:
            flash("Invalid username and/or password.", "danger")
            return render_template("accounts/login.html", form=form)
        
    return render_template("accounts/login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already registered.", "info")
        return redirect(url_for("index"))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("You registered and are now logged in. Welcome!", "success")

        return redirect(url_for("index"))

    return render_template("accounts/register.html", form=form)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    This view handles the file upload and saves the logs in the database and PC.
    """
    if request.method == "POST":
        file = request.files["file"]

        if file.filename == "":
            flash("No selected file", "warning")
            return redirect(url_for("index"))

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            filename, file_path = prepare_file(filename)
            file.save(file_path)                          # Save the file in the PC

            if filename.endswith((".txt", ".csv")):
                read_and_save_log_in_db(file_path)
                flash(f"File: {filename} uploaded successfully", "info")
                return redirect(url_for("index"))

            else:
                extracted_files, extracted_folder_path = unpack_archive(filename, file_path)

                for extracted_file in extracted_files:
                    extracted_file_path = os.path.join(extracted_folder_path, extracted_file)

                    if os.path.isfile(extracted_file_path):
                        read_and_save_log_in_db(extracted_file_path)

                os.remove(file_path)

                flash(f"File: {filename} uploaded successfully", "info")
                return redirect(url_for("index"))

        flash("Invalid file extension", "warning")
        return redirect(url_for("index"))

    return render_template("core/index.html")


@app.route("/search", methods=["GET", "POST"])
def search_logs():
    """
    This view handles the search of logs.
    """
    if request.method == "POST":

        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")
        order = request.form.get("order")
        keyword = request.form.get("keyword")

        start_date, end_date, error_message = time_validations(start_date_str, end_date_str)
        if error_message:
            flash(error_message, "warning")
            return redirect(url_for("search_logs"))

        if not start_date and not end_date and not keyword:
            flash("Please enter something to search.", "warning")
            return redirect(url_for("search_logs"))

        query = filter_logs(start_date, end_date, keyword, order)

        logs_data = [
            {
                "id": log.id,
                "date": log.date.strftime("%Y-%m-%d %H:%M:%S"),
                "content": log.content[:200] + "..." if len(log.content) > 200 else log.content
            } for log in query
        ]
        return render_template("core/search.html", logs=logs_data)
    return render_template("core/search.html")


@app.route("/log/<int:log_id>", methods=["GET"])
def log_detail(log_id):
    """
    This view handles the detail of a log.
    :param log_id: The id of the log.
    """
    log = Log.query.get(log_id)

    log_data = {
        "id": log.id,
        "date": log.date.strftime("%Y-%m-%d %H:%M:%S"),
        "content": log.content
    }
    return render_template("core/detail.html", log=log_data)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run()
