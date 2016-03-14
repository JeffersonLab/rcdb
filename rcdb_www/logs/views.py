from flask import Blueprint, render_template, g
from sqlalchemy import desc
from rcdb.model import LogRecord
from rcdb_www.pagination import Pagination

mod = Blueprint('logs', __name__, url_prefix='/logs')

PER_PAGE = 50


@mod.route('/', defaults={'page': 1})
@mod.route('/page/<int:page>')
def index(page):

    count = g.tdb.session.query(LogRecord).count()
    pagination = Pagination(page, PER_PAGE, count)

    log_records = g.tdb.session.query(LogRecord)\
                               .order_by(desc(LogRecord.id))\
                               .slice(pagination.item_limit_from, pagination.item_limit_to)

    return render_template("logs/index.html", log_records=log_records, pagination=pagination)

