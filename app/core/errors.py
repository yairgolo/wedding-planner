from flask import Blueprint, render_template

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(403)
def forbidden(_error):
    return render_template("errors/error.html", code=403, message="אין הרשאה לצפות בעמוד."), 403


@errors_bp.app_errorhandler(404)
def not_found(_error):
    return render_template("errors/error.html", code=404, message="העמוד שחיפשת לא נמצא."), 404


@errors_bp.app_errorhandler(500)
def server_error(_error):
    return render_template("errors/error.html", code=500, message="אירעה שגיאה פנימית."), 500
