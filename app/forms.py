from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, HiddenField, IntegerField, BooleanField, SubmitField, validators, \
    ValidationError, SelectField, TextAreaField, RadioField
from app import format_meso


def validate_fm_spot(form, field):
    if form.fm_channel.data != '0' and form.fm_door.data == '0':
        raise ValidationError('You must also select a door.')
    elif form.fm_channel.data == '0' and form.fm_door.data != '0':
        raise ValidationError('You must also select a channel.')


def validate_bid_range(form, field):
    m = 9999999999
    if not (form.request <= field.data <= m):
        raise ValidationError('Your bid must be between ' + format_meso(form.request) + ' and ' + format_meso(m))


def validate_reserve(form, field):
    if form.reserve_check.data is True:
        if field.data < 1 or field.data > 9999999999:
            raise ValidationError('Your reserve price must be between 1 and ' + format_meso(9999999999))


def validate_starting_bid(form, field):
    if field.data < 0 or field.data > 9999999998:
        raise ValidationError('Your starting bid must be between 0 and ' + format_meso(9999999998))


def validate_min_bid_inc(form, field):
    if form.starting_bid.data:
        starting = int(form.starting_bid.data)
        reserve = int(form.reserve.data) if form.reserve.data else 9999999999
        if field.data <= 0 or field.data > 1000000:
            raise ValidationError('Your minimum bid increment must be between 1 and ' + format_meso(1000000))
        elif field.data + starting >= reserve:
            raise ValidationError(
                'The sum of the minimum bid increment and starting bid must not be greater than or equal to the reserve.')


class BidForm(FlaskForm):
    amount = IntegerField('amount', [validate_bid_range],
                          render_kw={"placeholder": "",
                                     "class": "form-control form-control-sm input-element"})

    bid_btn = SubmitField('bid', [], render_kw={"class": "btn btn-success btn-sm",
                                                "value": "Bid"})


class ItemForm(FlaskForm):
    item_name = StringField(
        'item_name',
        [validators.DataRequired()],
        render_kw={"placeholder": "Search",
                   "class": "form-control form-control-lg"}
    )
    item_id = HiddenField('item_id')
    next_btn = SubmitField('next', [], render_kw={"class": "btn btn-block btn-primary btn-lg mb-3",
                                                  "value": "Next"})


class FindUserForm(FlaskForm):
    username = StringField(
        'username', [validators.DataRequired()],
        render_kw={"placeholder": "Search for Users", "class": "form-control"}
    )
    add_btn = SubmitField('add', [], render_kw={"class": "btn btn-primary",
                                                "value": "Message"})


class CommentForm(FlaskForm):
    comment = TextAreaField('comment', [validators.required(), validators.length(max=140, min=10)],
                            render_kw={"class": "form-control",
                                       "style": "min-height: 100px;"}
                            )
    comment_btn = SubmitField('comment_btn', [], render_kw={"class": "btn btn-secondary btn-md mb-3 mt-1",
                                                            "value": "Post comment"})


class FeedbackForm(FlaskForm):
    recp_id = HiddenField('recp_id')
    auc_id = HiddenField('auc_id')
    quality = HiddenField('quality')
    score = RadioField('score', choices=[('1', "Positive"), ('0', 'Neutral'), ('-1', 'Negative')], default='1')
    feedback = TextAreaField('feedback', [],
                             render_kw={"class": "form-control"}
                             )
    feedback_btn = SubmitField('feedback_btn', [], render_kw={"class": "btn btn-secondary btn-md mb-3 mt-1",
                                                              "value": "Leave feedback"})


class QuickMessageForm(FlaskForm):
    recp_id = HiddenField('recp_id')
    message = TextAreaField('message', [], render_kw={"class": "form-control"})
    send_btn = SubmitField('send_btn', [], render_kw={"class": "btn btn-secondary btn-md mb-3 mt-1",
                                                      "value": "Send message"})


class MessageForm(FlaskForm):
    message = TextAreaField('message', [validators.required(), validators.length(max=256, min=3)],
                            render_kw={"class": "form-control",
                                       "style": "height: 75px;"})
    send_btn = SubmitField('send_btn', [], render_kw={"class": "btn btn-success btn-md mb-3 mt-1",
                                                      "value": "Send"})


class AuctionForm(FlaskForm):
    item_id = HiddenField('item_id')
    tuc = HiddenField('tuc')
    int = IntegerField('INT', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    str = IntegerField('STR', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    luk = IntegerField('LUK', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    dex = IntegerField('DEX', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    watk = IntegerField('W.ATK', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    matk = IntegerField('M.ATK', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    eva = IntegerField('EVA', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    acc = IntegerField('ACC', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    wdef = IntegerField('W.DEF', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    mdef = IntegerField('M.DEF', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    hp = IntegerField('HP', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    mp = IntegerField('MP', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    speed = IntegerField('SPEED', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    jump = IntegerField('JUMP', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    slots = IntegerField('SLOTS', [], render_kw={"class": "form-control", "type": "number"}, default='0')
    upgrades = IntegerField('UPGRADES', [], render_kw={"class": "form-control", "type": "number"}, default='0')

    reserve = IntegerField('Reserve', [validate_reserve],
                           render_kw={"class": "form-control reserve-element"})
    reserve_check = BooleanField(label='reserve_check')
    starting_bid = IntegerField('Starting Bid', [validate_starting_bid],
                                render_kw={"class": "form-control starting-bid-element"},
                                default='0')
    min_bid_inc = IntegerField('Bid Increment', [validate_min_bid_inc, validators.required()],
                               render_kw={"class": "form-control min-bid-inc-element"},
                               default='1,000')
    fm_channel = SelectField(label='FM Spot', validators=[validate_fm_spot], choices=[('0', 'Channel'),
                                                                                      ('1', '1'), ('2', '2'),
                                                                                      ('3', '3'), ('4', '4'),
                                                                                      ('5', '5'), ('6', '6'),
                                                                                      ('7', '7'), ('8', '8'),
                                                                                      ('9', '9')],
                             render_kw={"class": "custom-select form-control"})
    fm_door = SelectField(label='', choices=[('0', 'Door'),
                                             ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'),
                                             ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'),
                                             ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'),
                                             ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'),
                                             ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'),
                                             ('21', '21'), ('22', '22')],
                          render_kw={"class": "custom-select form-control"})
    recaptcha = RecaptchaField()

    length = SelectField(label='Length', choices=[('12', '12 Hours'), ('24', '24 Hours'), ('48', '48 Hours'),
                                                  ('72', '72 Hours')],
                         render_kw={"class": "custom-select form-control"})

    submit = SubmitField('submit', [], render_kw={"class": "btn btn-block btn-primary btn-lg mb-3",
                                                  "value": "Post Auction"})
