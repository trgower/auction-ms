from flask import render_template, flash, redirect, request, jsonify, g
from app import app, db, models, fix_desc, format_meso, get_name_by_id, stat_dict
from flask_login import current_user
from flask_user import login_required
from datetime import datetime, timedelta
from sqlalchemy import func
from .forms import ItemForm, AuctionForm, BidForm, CommentForm, FeedbackForm, QuickMessageForm, MessageForm, \
    FindUserForm
from flask_paginate import Pagination
from collections import OrderedDict


@app.before_request
def send_alerts():
    if current_user.is_authenticated:
        alerts = models.Alerts.query.filter_by(user_id=current_user.id)
        for alert in alerts:
            flash(alert.message, alert.category)
            db.session.delete(alert)

        db.session.commit()


@app.route("/autocomplete")
def autocomplete():
    query = request.args.get('query')
    res = models.Strings.query.filter(models.Strings.name.like("%" + query + "%")).limit(10)
    results = [{"value": row.name, "id": row.id, "desc": fix_desc(row.desc) or "Equipment"} for row in res]
    return jsonify({"suggestions": results})


@app.route("/uac")
def auc():
    query = request.args.get('query')
    res = models.User.query.filter(models.User.username.like("%" + query + "%")).limit(5)
    results = [{"value": row.username, "desc": row.username} for row in res]
    return jsonify({"suggestions": results})


@app.route('/')
def index():
    new_auctions = models.Auctions.query.filter(models.Auctions.transaction_step == -1) \
        .order_by(models.Auctions.posted.desc()).limit(5).all()

    ending_soon = models.Auctions.query.filter(models.Auctions.transaction_step == -1) \
        .order_by(models.Auctions.end.asc()).limit(5).all()

    ha = models.HotAuctions.query.all()
    aucs = [auc.auction_id for auc in ha]
    hot_auctions = []
    for hauc in aucs:
        new = models.Auctions.query.filter((models.Auctions.id == hauc) & (models.Auctions.end > datetime.utcnow())).first()
        if new:
            hot_auctions.append(new)

    return render_template('index.html', hot_auctions=hot_auctions, new_auctions=new_auctions,
                           ending_soon=ending_soon)


@app.route('/auction/<auction_id>', methods=['GET', 'POST'])
def view_auction(auction_id):
    auction = models.Auctions.query.filter_by(id=auction_id).first()
    if not auction:
        return render_template('view_auction_not_found.html')

    feedback_query = auction.user.feedback
    pos = feedback_query.filter_by(score=1).count()
    neg = feedback_query.filter_by(score=-1).count()
    score = pos - neg
    perc = 0 if feedback_query.count() == 0 else round(
        (float(pos) / float(feedback_query.count())) * 100.0, 1)

    bid_form = BidForm()
    comment_form = CommentForm()
    maxbid = auction.bid
    maxbidder = auction.bids.first().bidder_id if auction.bids.first() else -1

    bid_offset_req = auction.min_bid_inc
    bid_form.request = maxbid + bid_offset_req
    if bid_form.bid_btn.data and bid_form.validate_on_submit():
        if current_user.is_authenticated:
            if current_user.id != maxbidder:
                if current_user.id != auction.seller_id:
                    if bid_form.amount.data == 9999999999:
                        auction.end = datetime.utcnow()
                    new_bid = models.Bids(
                        bidder_id=current_user.id, auction_id=auction_id, amount=bid_form.amount.data,
                        posted=datetime.utcnow())
                    auction.bid = new_bid.amount
                    w = models.Watchlists.query.filter_by(watcher_id=current_user.id, auction_id=auction.id).first()
                    if not w:
                        watchlist = models.Watchlists(
                            watcher_id=current_user.id, auction_id=auction.id,
                            posted=datetime.utcnow())
                        db.session.add(watchlist)

                    if maxbidder != -1:
                        outbid_alert = models.Alerts(
                            user_id=maxbidder,
                            message='You were outbid on <a href="/auction/' + str(auction.id) +
                                    '">' + auction.strings.name + '</a> by <a href="/u/' + str(current_user.id) + '">' +
                                    current_user.username + '</a> with a bid of <strong><img src="/static/images/meso_large.png" alt="" width="18px">' +
                                    format_meso(auction.bid) + '</strong>.',
                            category='warning')
                        db.session.add(outbid_alert)

                    db.session.add(new_bid)
                    db.session.commit()

                    flash('Bid of ' + format_meso(
                        bid_form.amount.data) + ' was accepted! This item was automatically added to your watch list.',
                          'success')
                    return redirect(request.path)
                else:
                    flash('You cannot bid on your own auction!', 'danger')
            else:
                flash('You are already the max bidder!', 'danger')
        else:
            flash('You must be logged in to do that!', 'danger')
    elif comment_form.comment_btn.data and comment_form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = models.Comments(
                commenter_id=current_user.id, auction_id=auction_id,
                message=comment_form.comment.data, posted=datetime.utcnow())
            db.session.add(new_comment)
            db.session.commit()

            comment_form.comment.data = ''
            flash('Comment posted!', 'success')
            return redirect(request.path)
        else:
            flash('You must be logged in to do that!', 'danger')

    comment_p = request.args.get('c', type=int, default=1)
    comments_query = auction.comments.order_by(models.Comments.posted.desc())
    comments = comments_query.paginate(comment_p, 5).items
    comments_page = Pagination(
        page_parameter='c', c=comment_p, total=comments_query.count(), search=False,
        record_name='comments', per_page=5,
        bs_version=3, alignment='justify-content-center mb-0 mt-2', link_size='sm')

    bid_p = request.args.get('b', type=int, default=1)
    bids_query = auction.bids.order_by(models.Bids.amount.desc())
    bids = bids_query.paginate(bid_p, 5).items
    bid_page = Pagination(
        page_parameter='b', b=bid_p, total=bids_query.count(), search=False,
        record_name='bids', per_page=5,
        bs_version=3, alignment='justify-content-center mb-0 mt-2', link_size='sm')

    seller = auction.user.username

    if auction.end < datetime.utcnow():
        return render_template(
            'view_auction_ended.html', auction=auction, sel=seller, comments_page=comments_page,
            bid_page=bid_page, max_bid=maxbid, comments=comments, bids=bids,
            comments_num=comments_query.count(), bid_num=bids_query.count(),
            percent=perc, score=score)

    if not current_user.is_authenticated:
        return render_template(
            'view_auction_anon.html', auction=auction, sel=seller, comments_page=comments_page,
            bid_page=bid_page, max_bid=maxbid, comments=comments, bids=bids,
            comments_num=comments_query.count(), bid_num=bids_query.count(),
            percent=perc, score=score)

    return render_template(
        'view_auction_auth.html', auction=auction, user=current_user, bid_form=bid_form, sel=seller,
        bid_off=bid_offset_req, bids=bids, max_bid=maxbid,
        bid_num=bids_query.count(), bid_page=bid_page, comment_form=comment_form,
        comments_num=comments_query.count(), comments_page=comments_page, comments=comments,
        percent=perc, score=score)


@app.route('/post', methods=['GET', 'POST'])
@login_required
def post_auction():
    item_form = ItemForm()
    if request.method != 'POST':
        return render_template('find_item.html', item_form=item_form)

    auction_form = AuctionForm()
    item = None
    equip = None

    if auction_form.submit.data and auction_form.validate_on_submit():
        time_now = datetime.utcnow()
        time_delta = timedelta(hours=int(auction_form.length.data))
        new_auction = models.Auctions(
            seller_id=current_user.id,
            item_id=int(auction_form.item_id.data),
            starting_bid=int(auction_form.starting_bid.data),
            min_bid_inc=int(auction_form.min_bid_inc.data),
            bid=int(auction_form.starting_bid.data),
            fm_channel=int(auction_form.fm_channel.data),
            fm_door=int(auction_form.fm_door.data),
            length=int(auction_form.length.data),
            posted=time_now, end=time_now + time_delta)

        if auction_form.reserve_check.data:
            new_auction.reserve = int(auction_form.reserve.data)

        if int(auction_form.item_id.data) < 2000000:
            equip = models.Equipment.query.filter_by(id=new_auction.item_id).first()
            increased = 0
            for i, v in stat_dict.items():
                field = auction_form[v]
                if field.data and int(field.data) > 0:
                    if field.name == 'hp' or field.name == 'mp':
                        increased = increased + int((int(field.data) - equip.get_dict()[field.name]) / 10)
                    elif field.name != 'slots' and field.name != 'upgrades':
                        increased = increased + (int(field.data) - equip.get_dict()[field.name])
                    setattr(new_auction, v, int(field.data))

            new_auction.item_quality = get_item_quality(increased, int(auction_form.upgrades.data))

        db.session.add(new_auction)
        db.session.commit()
        flash('Your auction has been posted!', 'success')
        return redirect('/post')

    elif auction_form.item_id.data or (item_form.next_btn.data and item_form.validate_on_submit()):
        item_id = int(item_form.item_id.data)
        item = models.Strings.query.filter_by(id=item_id).first()
    if item is None:
        flash('Invalid Item ID', 'danger')
        return redirect('/post')

    auction_form.item_id.data = item_id
    if item.id < 2000000:
        equip = models.Equipment.query.filter_by(id=item_id).first()
        auction_form.tuc.data = equip.tuc
        scroll_id = '204'
        equip_digits = int(item_id / 10000) - 100
        equip_digits = '%02d' % equip_digits
        scroll_id = scroll_id + equip_digits
        scrolls = models.Scroll.query.filter(models.Scroll.id.like(scroll_id + '%')).all()

        for scroll in scrolls:
            for col in scroll.get_dict().items():
                if col[1] > 0:
                    auction_form[col[0]].description = True

        for col in equip.get_dict().items():
            if col[1] > 0 or col[0] == 'upgrades':
                auction_form[col[0]].description = True
                auction_form[col[0]].data = col[1]

        item.desc = '' \
                    + str(equip.reqlevel) + ' LVL, ' \
                    + str(equip.reqstr) + ' STR, ' \
                    + str(equip.reqdex) + ' DEX, ' \
                    + str(equip.reqint) + ' INT, ' \
                    + str(equip.reqluk) + ' LUK'

    if equip:
        return render_template('post_auction_equip.html', item=item, equip=equip, auction_form=auction_form)

    return render_template('post_auction_item.html', item=item, auction_form=auction_form)


@app.route('/search')
def search():
    query = None
    sort = None
    results_per_page = 10
    pagination = None
    failed = False
    query_list = None
    sort_by = OrderedDict()
    if len(request.args.get('query')) < 3:
        failed = True
    elif request.args.get('query'):
        page = request.args.get('p', type=int, default=1)
        query = request.args.get('query')
        res = models.Strings.query.filter(models.Strings.name.like('%' + query + '%')).all()
        search_item_ids = [row.id for row in res]
        query_list = None
        if res:
            query_results = models.Auctions.query.filter(models.Auctions.item_id.in_(search_item_ids) &
                                                         (models.Auctions.end > datetime.utcnow()))
            sort_by.update({'Name': 'name'})
            sort_by.update({'Highest Price': 'hprice'})
            sort_by.update({'Lowest Price': 'lprice'})
            sort_by.update({'Ending Soon': 'end'})
            sort_by.update({'Recent Post': 'recent'})
            for row in query_results.all():
                for i, v in stat_dict.items():
                    if getattr(row, v) is not None and getattr(row, v) > 0 and v not in sort_by.values():
                        sort_by.update({i: v})

            sort = request.args.get('sort')
            if sort and sort in sort_by.values():
                if sort == 'name':
                    query_results = query_results.join(models.Strings.auctions).order_by(models.Strings.name)
                elif sort == 'hprice':
                    query_results = query_results.order_by(models.Auctions.bid.desc())
                elif sort == 'lprice':
                    query_results = query_results.order_by(models.Auctions.bid.asc())
                elif sort == 'end':
                    query_results = query_results.order_by(models.Auctions.end.asc())
                elif sort == 'recent':
                    query_results = query_results.order_by(models.Auctions.end.desc())
                else:
                    query_results = query_results.order_by(models.Auctions.__table__.c[sort].desc())
            query_count = query_results.count()
            query_list = query_results.paginate(page, results_per_page).items
            pagination = Pagination(
                page_parameter='p', p=page, total=query_count, search=False,
                record_name='auctions', per_page=results_per_page,
                bs_version=3, alignment='justify-content-end')
    elif request.args.get('query') is None:
        failed = True

    return render_template(
        'search.html', term=query, res=query_list,
        pagination=pagination, failed=failed, sort_by=sort_by, sort=sort, query=query)


@app.route('/feedback/<username>')
def view_user_feedback(username):
    u = models.User.query.filter_by(username=username).first()
    if not u:
        return render_template('view_user_not_found.html')

    feedback_query = u.feedback.order_by(models.Feedback.posted.desc())
    p = request.args.get('a', type=int, default=1)
    feedback = feedback_query.paginate(p, 15).items
    feedback_page = Pagination(
        page_parameter='p', p=p, total=feedback_query.count(), search=False,
        record_name='review', per_page=15, bs_version=3,
        alignment='justify-content-center mt-0 mb-0',
        link_size='sm')

    pos = feedback_query.filter_by(score=1).count()
    neg = feedback_query.filter_by(score=-1).count()
    score = pos - neg
    perc = 0 if feedback_query.count() == 0 else round(
        (float(pos) / float(feedback_query.count())) * 100.0, 1)

    return render_template(
        'view_user_feedback.html', u=u, feedback=feedback, feedback_percentage=perc,
        feedback_score=score, feedback_count=pos + neg, feedback_page=feedback_page)


@app.route('/u/<username>', methods=['GET', 'POST'])
def view_user(username):
    u = models.User.query.filter_by(username=username).first()
    if not u:
        return render_template('view_user_not_found.html')

    message_form = QuickMessageForm()

    if message_form.send_btn.data and message_form.validate_on_submit():
        if 2 <= len(message_form.message.data) <= 64:
            message = models.Messages(
                sender_id=current_user.id, recp_id=u.id,
                message=str(message_form.message.data), sent=datetime.utcnow())
            db.session.add(message)
            db.session.commit()
            flash('Your message was sent to ' + u.username, 'success')
            return redirect(request.path)
        else:
            flash('Your message must be between 2 and 64 characters long.', 'danger')

    auction_query = u.auctions.filter(models.Auctions.end > datetime.utcnow()).order_by(models.Auctions.posted.asc())

    a = request.args.get('a', type=int, default=1)
    auctions = auction_query.paginate(a, 4).items
    auction_page = Pagination(
        page_parameter='a', a=a, total=auction_query.count(), search=False,
        record_name='auctions', per_page=4, bs_version=3,
        alignment='justify-content-center mt-0 mb-0',
        link_size='sm')

    feedback_query = u.feedback.order_by(models.Feedback.posted.desc())
    pos = feedback_query.filter_by(score=1).count()
    neg = feedback_query.filter_by(score=-1).count()
    score = pos - neg
    perc = 0 if feedback_query.count() == 0 else round(
        (float(pos) / float(feedback_query.count())) * 100.0, 1)
    feedback = feedback_query.limit(3)
    return render_template(
        'view_user.html', u=u, current_auctions=auctions, auction_page=auction_page,
        feedback=feedback, feedback_percentage=perc,
        feedback_score=score, feedback_count=pos + neg, current_user=current_user,
        message_form=message_form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def view_dashboard():
    feedback_form = FeedbackForm()
    message_form = QuickMessageForm()

    if feedback_form.feedback_btn.data and feedback_form.validate_on_submit():
        if 10 <= len(feedback_form.feedback.data) <= 50:
            auc = models.Auctions.query.filter_by(id=int(feedback_form.auc_id.data)).first()
            if auc.transaction_step == 0:
                if auc.buyer_id == current_user.id:
                    auc.transaction_step = 2
                elif auc.seller_id == current_user.id:
                    auc.transaction_step = 1
            else:
                auc.transaction_step = 3
            feedback = models.Feedback(
                reviewer=current_user.id, reviewee=int(feedback_form.recp_id.data),
                auction_id=int(feedback_form.auc_id.data), score=int(feedback_form.score.data),
                message=str(feedback_form.feedback.data), posted=datetime.utcnow())
            db.session.add(feedback)
            db.session.commit()
            flash('Your feedback for ' + get_name_by_id(int(feedback_form.recp_id.data)) + ' has been submitted!',
                  'success')
            return redirect(request.path)
        else:
            flash('Feedback message must be between 10 and 50 characters long.', 'danger')

    if message_form.send_btn.data and message_form.validate_on_submit():
        if 2 <= len(message_form.message.data) <= 64:
            message = models.Messages(
                sender_id=current_user.id, recp_id=int(message_form.recp_id.data),
                message=str(message_form.message.data), sent=datetime.utcnow())
            db.session.add(message)
            db.session.commit()
            flash('Your message was sent to ' + get_name_by_id(int(feedback_form.recp_id.data)),
                  'success')
            return redirect(request.path)
        else:
            flash('Your message must be between 2 and 64 characters long.', 'danger')

    u = current_user

    auction_query = u.auctions.filter((models.Auctions.seller_id == u.id) & (models.Auctions.transaction_step == -1))
    a = request.args.get('a', type=int, default=1)
    auctions = auction_query.paginate(a, 5).items
    auction_page = Pagination(
        page_parameter='a', a=a, total=auction_query.count(), search=False,
        record_name='auctions', per_page=5, bs_version=3,
        alignment='justify-content-center',
        link_size='sm')

    messages_query = models.Messages.query.filter((models.Messages.sender_id == u.id) |
                                                  (models.Messages.recp_id == u.id)).order_by(
        models.Messages.sent.desc())
    messages = reversed(messages_query.limit(8).all())

    time_delta = timedelta(days=7)
    recent_query = models.Auctions.query.filter(
        (models.Auctions.end >= datetime.utcnow() - time_delta) & (
            (models.Auctions.buyer_id == u.id) | (models.Auctions.seller_id == u.id)) &
        (models.Auctions.transaction_step >= 0)).order_by(models.Auctions.transaction_step.asc()).order_by(
        models.Auctions.end.desc())
    r = request.args.get('r', type=int, default=1)
    recent = recent_query.paginate(r, 3).items
    recent_page = Pagination(
        page_parameter='r', r=r, total=recent_query.count(), search=False,
        record_name='auctions', per_page=3, bs_version=3,
        alignment='justify-content-center mt-0 mb-0',
        link_size='sm')

    unsold_query = models.Auctions.query.filter(
        (models.Auctions.seller_id == u.id) &
        (models.Auctions.transaction_step < -1)).order_by(models.Auctions.end.desc())
    f = request.args.get('f', type=int, default=1)
    unsold = unsold_query.paginate(f, 5).items
    unsold_page = Pagination(
        page_parameter='f', f=f, total=unsold_query.count(), search=False,
        record_name='auctions', per_page=5, bs_version=3,
        alignment='justify-content-center mt-0 mb-0',
        link_size='sm')

    watch_query = models.Auctions.query.join(models.Watchlists).filter_by(watcher_id=u.id)
    w = request.args.get('w', type=int, default=1)
    watchlist = watch_query.paginate(w, 5).items
    watch_page = Pagination(
        page_parameter='w', w=w, total=unsold_query.count(), search=False,
        record_name='auctions', per_page=5, bs_version=3,
        alignment='justify-content-center mt-0 mb-0',
        link_size='sm')

    feedback_query = u.feedback
    pos = feedback_query.filter_by(score=1).count()
    neg = feedback_query.filter_by(score=-1).count()
    score = pos - neg
    perc = 0 if feedback_query.count() == 0 else round(
        (float(pos) / float(feedback_query.count())) * 100.0, 1)

    return render_template(
        'dashboard.html', u=u, current_auctions=auctions, auction_page=auction_page,
        recent_activity=recent, recent_page=recent_page, feedback_form=feedback_form,
        messages=messages, feedback_percentage=perc, feedback_score=score,
        message_form=message_form, unsold=unsold, unsold_page=unsold_page,
        watchlist=watchlist, watch_page=watch_page)


@app.route('/cancel/<aucid>')
@login_required
def cancel_auction(aucid):
    aucid = int(aucid)
    auction = models.Auctions.query.filter_by(id=aucid).first()
    if not auction:
        flash("Strange that you're trying to cancel an auction that doesn't exist...", 'warning')
        return redirect('/dashboard/')

    if auction.bids.count() > 0:
        flash("Why would you want to do that? These people depend on you.", 'warning')
        return redirect('/dashboard/')

    db.session.delete(auction)
    db.session.commit()

    flash('Auction cancelled.', 'success')
    return redirect('/dashboard')


@app.route('/deleteconv/<convo>')
@login_required
def delete_conversation(convo):
    convo = int(convo)
    conversation = models.Conversations.query.filter_by(id=convo).first()
    if not conversation:
        return redirect('/messages')

    db.session.delete(conversation)
    db.session.commit()

    flash('Conversation deleted.', 'success')
    return redirect('/messages')


@app.route('/early/<aucid>')
@login_required
def early_auction(aucid):
    aucid = int(aucid)
    auction = models.Auctions.query.filter_by(id=aucid).first()
    if not auction:
        flash("That auction doesn't exist. I know what you're up to", 'warning')
        return redirect('/dashboard/')

    if auction.bids.count() == 0:
        flash("Now I'm just confused", 'warning')
        return redirect('/dashboard/')

    maxbid = models.Bids.query.filter_by(auction_id=auction.id).order_by(models.Bids.amount.desc()).first()
    auction.buyer_id = maxbid.bidder_id
    auction.end = datetime.utcnow()
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

    db.session.commit()

    flash('Auction ended early.', 'success')
    return redirect('/dashboard')


@app.route('/watch/<aucid>')
@login_required
def watch_auction(aucid):
    aucid = int(aucid)
    auction = models.Auctions.query.filter_by(id=aucid).first()
    if not auction:
        flash("I don't see an auction, do you?", 'warning')
        return redirect('/auction/' + str(aucid))
    if auction.seller_id == current_user.id:
        flash("Why would you want to do that?", 'warning')
        return redirect('/auction/' + str(aucid))
    w = models.Watchlists.query.filter_by(watcher_id=current_user.id, auction_id=auction.id).first()
    if w:
        db.session.delete(w)
        db.session.commit()
        flash("You have removed the item from your watch list.", 'warning')
        return redirect('/dashboard')

    watchlist = models.Watchlists(watcher_id=current_user.id, auction_id=auction.id, posted=datetime.utcnow())

    db.session.add(watchlist)
    db.session.commit()

    flash('The item was added to your watchlist!', 'success')
    return redirect('/auction/' + str(aucid))


@app.route('/messages/<conversation>', methods=['GET', 'POST'])
@app.route('/messages', defaults={'conversation': None}, methods=['GET', 'POST'])
@login_required
def messages(conversation):
    if not conversation:
        add_convo = FindUserForm()

        if add_convo.validate_on_submit():
            return redirect(request.path + '/' + str(add_convo.username.data))

        conversations = models.Conversations.query.filter_by(user_id=current_user.id).order_by(
            models.Conversations.last_msg.desc())
        c = request.args.get('c', type=int, default=1)
        convos = conversations.paginate(c, 10).items
        convo_page = Pagination(
            page_parameter='c', c=c, total=conversations.count(), search=False,
            record_name='conversations', per_page=10, bs_version=3,
            alignment='justify-content-center mt-0 mb-0',
            link_size='sm')
        return render_template('messages.html', conversations=convos, convo_page=convo_page, add_convo=add_convo)

    conversant = models.User.query.filter_by(username=conversation).first()
    if not conversant:
        return "User not found"

    message_form = MessageForm()

    if message_form.validate_on_submit():
        convo = models.Conversations.query.filter_by(user_id=current_user.id, conversant=conversant.id).first()
        if not convo:
            convo = models.Conversations(
                user_id=current_user.id, conversant=conversant.id, created=datetime.utcnow())
            db.session.add(convo)
        c_convo = models.Conversations.query.filter_by(user_id=conversant.id, conversant=current_user.id).first()
        if not c_convo:
            c_convo = models.Conversations(
                user_id=conversant.id, conversant=current_user.id, created=datetime.utcnow())
            db.session.add(c_convo)
        sent = datetime.utcnow()
        c_convo.last_msg = sent
        convo.last_msg = sent
        convo.last_read = sent
        message = models.Messages(
            sender_id=current_user.id, recp_id=conversant.id,
            message=str(message_form.message.data), sent=sent)
        db.session.add(message)
        db.session.commit()
        return redirect(request.path)

    convo = models.Conversations.query.filter_by(user_id=current_user.id, conversant=conversant.id).first()

    limit = request.args.get('limit', type=int, default=15)
    total = 0

    messages = None
    if convo:
        messages = models.Messages.query.filter(
            (((models.Messages.sender_id == current_user.id) & (models.Messages.recp_id == conversant.id)) |
             ((models.Messages.sender_id == conversant.id) & (models.Messages.recp_id == current_user.id))) &
            (models.Messages.sent >= convo.created)
        ).order_by(models.Messages.sent.desc())
        total = messages.count()
        messages = list(reversed(messages.limit(limit).all()))
        convo.last_read = datetime.utcnow()
        db.session.commit()

    load_more = min(10, total - limit)

    return render_template('conversation.html', messages=messages, c_name=conversant.username, msg_form=message_form,
                           moremsg=total > limit, limit=limit, load_more=load_more)


def get_item_quality(increased, upgrades):
    if increased >= 40:
        return 4
    elif increased >= 23:
        return 3
    elif increased >= 6:
        return 2
    elif increased >= 0 and upgrades > 0:
        return 1
    elif increased >= 0:
        return 0
    else:
        return -1
