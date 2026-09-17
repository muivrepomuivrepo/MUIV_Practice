from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app.domain.user import User
from app.extensions import db


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("client.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            if user.is_admin():
                return redirect(url_for("admin.dashboard"))
            if user.is_manager():
                return redirect(url_for("manager.dashboard"))
            return redirect(url_for("client.dashboard"))
        flash("Неверный логин или пароль.", "danger")
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("client.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        company = request.form.get("company", "").strip()
        password = request.form.get("password", "")
        if not username or not email or not full_name or not password:
            flash("Заполните обязательные поля.", "danger")
            return render_template("register.html")
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Пользователь с таким логином или почтой уже существует.", "danger")
            return render_template("register.html")
        user = User(username=username, email=email, full_name=full_name, phone=phone, company=company, role="client")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Регистрация завершена. Выполните вход.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("public.index"))
