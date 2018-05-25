from collections import OrderedDict
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timedelta
from celery import Celery

app = Flask(__name__)
app.config.from_object('config')

stat_dict = OrderedDict(
    [('W.ATK', 'watk'), ('M.ATK', 'matk'), ('INT', 'int'), ('STR', 'str'), ('LUK', 'luk'), ('DEX', 'dex'),
     ('EVA', 'eva'), ('ACC', 'acc'), ('W.DEF', 'wdef'), ('M.DEF', 'mdef'), ('HP', 'hp'), ('MP', 'mp'),
     ('SPEED', 'speed'), ('JUMP', 'jump'), ('SLOTS', 'slots'), ('UPGRADES', 'upgrades')])


@app.template_filter('meso')
def format_meso(meso):
    return str("{:,}".format(meso))


@app.template_filter('trimdesc')
def trim_desc(desc):
    if len(desc) > 128:
        return desc[:128] + ' ...'
    return desc


@app.template_filter('trimname')
def trim_name(name):
    if len(name) > 32:
        return name[:32] + ' ...'
    return name


@app.template_filter('auctionstats')
def get_auction_item_stats(auction):
    item_stats = ''
    for i, v in stat_dict.iteritems():
        if getattr(auction, v) > 0 and v != 'upgrades':
            if item_stats == '':
                item_stats = item_stats + str(getattr(auction, v)) + ' ' + i
            else:
                item_stats = item_stats + ', ' + str(getattr(auction, v)) + ' ' + i
    return item_stats


@app.template_filter('separatemsg')
def separatemsg(last, curr):
    time_delta = curr.sent - last.sent
    return (time_delta.seconds / 60) > 15


@app.template_filter('newmsg')
def newmsg(user):
    conversations = models.Conversations.query.filter_by(user_id=user.id).order_by(
        models.Conversations.last_msg.desc()).first()
    return conversations and (not conversations.last_read or (conversations.last_read < conversations.last_msg))


@app.template_filter('itemupgrades')
def get_auction_item_upgrades(auction):
    return '' if auction.upgrades <= 0 else ' (+' + str(auction.upgrades) + ')'


@app.template_filter('getscore')
def get_score(userid):
    feedback_query = models.Feedback.query.filter_by(reviewee=userid)
    pos = feedback_query.filter_by(score=1).count()
    neg = feedback_query.filter_by(score=-1).count()
    score = pos - neg
    return score


@app.template_filter('getpercent')
def get_percent(userid):
    feedback_query = models.Feedback.query.filter_by(reviewee=userid)
    pos = feedback_query.filter_by(score=1).count()
    perc = 0 if feedback_query.count() == 0 else round(
        (float(pos) / float(feedback_query.count())) * 100.0, 1)
    return perc


@app.template_filter('fixdesc')
def fix_desc(desc):
    desc = desc.replace("\\n", " ")
    desc = desc.replace("\\r", "")
    desc = desc.replace("#c", "")
    desc = desc.replace("#", "")
    return desc


@app.template_filter('getname')
def get_name_by_id(user_id):
    user = models.User.query.filter_by(id=user_id).first()
    return user.username if user else 'Not found'


@app.template_filter('lastmsg')
def lastmsg(convo):
    msg = models.Messages.query.filter(
        (((models.Messages.sender_id == convo.user_id) & (models.Messages.recp_id == convo.conversant)) |
         ((models.Messages.sender_id == convo.conversant) & (models.Messages.recp_id == convo.user_id))) &
        (models.Messages.sent >= convo.created)
    ).order_by(models.Messages.sent.desc()).first()
    ret = ""
    if msg.sender_id == convo.user_id:
        ret = "You: "
    ret = ret + msg.message
    return ret


@app.template_filter('timesince')
def get_time_since(posted):
    time = ''
    time_delta = datetime.utcnow() - posted
    if time_delta.days > 0:
        time = str(time_delta.days) + 'd '

    if time_delta.seconds / 60 / 60 > 0:
        time = time + str(time_delta.seconds / 60 / 60) + 'h '
        if time.count(' ') >= 2:
            return time + 'ago'

    if time_delta.seconds / 60 % 60 > 0:
        time = time + str(time_delta.seconds / 60 % 60) + 'm '
        if time.count(' ') >= 2:
            return time + 'ago'

    if time_delta.seconds > 0:
        time = time + str(time_delta.seconds % 60) + 's '
        if time.count(' ') >= 2:
            return time + 'ago'

    return time + 'ago' if len(time) > 0 else 'just now'


@app.template_filter('timeleft')
def get_time_left(end):
    time = ''
    if end < datetime.utcnow():
        return 'ended'
    time_delta = end - datetime.utcnow()
    if time_delta.days > 0:
        time = str(time_delta.days) + 'd '

    if time_delta.seconds / 60 / 60 > 0:
        time = time + str(time_delta.seconds / 60 / 60) + 'h '
        if time.count(' ') >= 2:
            return time + 'left'

    if time_delta.seconds / 60 % 60 > 0:
        time = time + str(time_delta.seconds / 60 % 60) + 'm '
        if time.count(' ') >= 2:
            return time + 'left'

    if time_delta.seconds > 0:
        time = time + str(time_delta.seconds % 60) + 's '
        if time.count(' ') >= 2:
            return time + 'left'

    return time + 'left'


@app.template_filter('msgtime')
def msgtime(msg):
    if datetime.utcnow().day == msg.sent.day:
        return "Today at " + msg.sent.strftime("%I:%M%p")
    else:
        return msg.sent.strftime("%m/%e/%Y")


app.jinja_env.filters['getname'] = get_name_by_id
app.jinja_env.filters['timesince'] = get_time_since
app.jinja_env.filters['timeleft'] = get_time_left
app.jinja_env.filters['fixdesc'] = fix_desc
app.jinja_env.filters['auctionstats'] = get_auction_item_stats
app.jinja_env.filters['itemupgrades'] = get_auction_item_upgrades
app.jinja_env.filters['meso'] = format_meso
app.jinja_env.filters['trimdesc'] = trim_desc
app.jinja_env.filters['getscore'] = get_score
app.jinja_env.filters['getpercent'] = get_percent
app.jinja_env.filters['lastmsg'] = lastmsg
app.jinja_env.filters['newmsg'] = newmsg
app.jinja_env.filters['separatemsg'] = separatemsg

csrf = CSRFProtect()
csrf.init_app(app)

db = SQLAlchemy(app)

mail = Mail(app)


def make_celery(app):
    celeryy = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                     broker=app.config['CELERY_BROKER_URL'])
    celeryy.conf.update(app.config)
    TaskBase = celeryy.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celeryy.Task = ContextTask
    return celeryy


celery = make_celery(app)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(3, end_auctions, name='end_auctions')


@celery.task
def end_auctions():
    auctions = models.Auctions.query.filter(
        (models.Auctions.end <= datetime.utcnow()) & (models.Auctions.transaction_step == -1)
    )
    for auction in auctions:
        maxbid = models.Bids.query.filter_by(auction_id=auction.id).order_by(models.Bids.amount.desc()).first()
        if maxbid:
            if maxbid.amount >= auction.reserve:
                auction.buyer_id = maxbid.bidder_id
                auction.transaction_step = 0
                buyer = models.User.query.filter_by(id=auction.buyer_id).first()
                seller = models.User.query.filter_by(id=auction.seller_id).first()
                sold_alert = models.Alerts(
                    user_id=auction.seller_id,
                    message='Your <a href="/auction/' + str(auction.id) +
                            '">' + auction.strings.name + '</a> sold to <a href="/u/' + str(auction.buyer_id) + '">' +
                            buyer.username + '</a> for <strong><img src="/static/images/meso_large.png" alt="" width="18px">' +
                            format_meso(maxbid.amount) + '</strong>.',
                    category='success')
                bought_alert = models.Alerts(
                    user_id=auction.buyer_id,
                    message='You won a(n) <a href="/auction/' + str(auction.id) +
                            '">' + auction.strings.name + '</a> from <a href="/u/' + str(auction.buyer_id) + '">' +
                            seller.username + '</a> with a max bid of <strong><img src="/static/images/meso_large.png" alt="" width="18px">' +
                            format_meso(maxbid.amount) + '</strong>.',
                    category='success')
                db.session.add(sold_alert)
                db.session.add(bought_alert)
                # Trigger sold notification
                # Trigger bought notification
            else:
                auction.transaction_step = -3
                unsold_reserve = models.Alerts(
                    user_id=auction.seller_id,
                    message='Your <a href="/auction/' + str(auction.id) +
                            '">' + auction.strings.name + '</a> did not sell because it did not reach the reserve price of <strong><img src="/static/images/meso_large.png" alt="" width="18px">' +
                            format_meso(maxbid.amount) + '</strong>.',
                    category='danger')
                db.session.add(unsold_reserve)
        else:
            auction.transaction_step = -2
            unsold = models.Alerts(
                user_id=auction.seller_id,
                message='Your <a href="/auction/' + str(auction.id) +
                        '">' + auction.strings.name + '</a> ended with 0 bids! Sorry about that.',
                category='danger')
            db.session.add(unsold)

    ending_auctions = models.Auctions.query.filter(models.Auctions.transaction_step == -1) \
        .order_by(models.Auctions.end.asc()).limit(5000).all()

    if ending_auctions:
        d = {}
        for auc in ending_auctions:
            count = auc.bids.count()
            time_delta = datetime.utcnow() - auc.posted
            auc_hours = time_delta.seconds / 60 / 60
            d[auc] = float(count) if auc_hours < 1 else float(count) / float(auc_hours)

        aucs = [auc for auc in ending_auctions]
        aucs.sort(key=d.get, reverse=True)

        hot_auctions = models.HotAuctions.query.order_by(models.HotAuctions.id.asc()).all()
        i = 0
        for auc in hot_auctions:
            auc.auction_id = 0 if i >= len(aucs) else aucs[i].id
            i = i + 1

        db.session.commit()


    if auctions:
        db.session.commit()


from app import views, models
