var queueData = data.queue;
var upvoteData = data.upvotes;
var responseUpvotes = data.upvotes2;
var flagData = data.flags;
var autorefresh = true;

var today = new Date();
var notViewedGuidelines = true;

// Word banks
var channelRef = {
    rendell: ['rendell', 'banzon', 'rtbanzon']
}

var common = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'will', 'an', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'when', 'me', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take', 'person', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'];

function refreshPage() {
    endTime = new Date();

    Notify('Connection timed out. Refreshing page in 5 seconds. Click here to stop refresh.', 
        function () { 
            Notify('Refresh cancelled. You\'ll need to manually refresh to reconnect.', null, null, 'success');
            autorefresh = false;
        }, null, 'warning');
    window.setInterval(function() {
        if(autorefresh) {
            window.location.reload();   
        }
    }, 5000);
}

function totalFeedbackUpvotes(uuid) {
    total = 0;

    for(var x = 0; x < upvoteData.length; x++) {
        if(upvoteData[x].uuid == uuid) {
            total += 1;
        }
    }

    return total;
}

function getDifference(date1, date2) {
    var diffMs = (date2 - date1);
    var diffDays = Math.floor(diffMs / 86400000);

    return diffDays;
}

function totalResponseUpvotes(uuid) {
    total = 0;

    for(var x = 0; x < responseUpvotes.length; x++) {
        if(responseUpvotes[x].uuid == uuid) {
            total += 1;
        }
    }

    return total;
}

function createCard(uuid, created, queue, feedback, response, num, upvotes, upvotes2, level, inquirer, updated, response_uuid) {
    if(response == null || response == '') {
        card = $('#feedback-template').html().toString();
    } else {
        card = $('#feedback-answered-template').html().toString();
    }

    switch(level) {
        case 2:
            levelBg = '#aed6f1';
            break;
        case 3:
            levelBg = '#d2b4de';
            break;
        case 4:
            levelBg = '#ffaaaa';
            break;
        default:
            levelBg = 'yellow';
    }

    infoBubble = ''
    if(inquirer != 'anonymous') {
        infoBubble = '<i class="fa fa-info-circle infoBubble mr-2" data-toggle="tooltip" data-placement="top" title="' + inquirer + '" aria-hidden="true"></i>';
    }

    card = card.replace('%created%', created);
    card = card.replace('%updated%', updated);
    card = card.replace('%feedback%', feedback);
    card = card.replace('%response%', response);
    card = card.replace('%response-uuid%', response_uuid);
    card = card.replace('%level%', 'L' + level);
    card = card.replace('%level-bg%', levelBg);
    card = card.replace('%identified%', infoBubble);
    card = card.replace(new RegExp('%uuid%', 'g'), uuid);
    card = card.replace(new RegExp('%num%', 'g'), num);
    card = card.replace(new RegExp('%feedback-upvotes%', 'g'), upvotes);
    card = card.replace(new RegExp('%response-upvotes%', 'g'), upvotes2);
    card = card.replace(new RegExp('%response-uuid%', 'g'), response_uuid);

    createDate = new Date(created.split(' ')[0]);
    daysPassed = getDifference(createDate, today);
    slaBar = (daysPassed / 7 * 100);
    slaColor = 'info';
    if(slaBar > 75) {
        slaColor = 'warning';
    }

    if(slaBar > 100) {
        slaBar = 100;
        slaColor = 'danger';
    }

    card = card.replace(new RegExp('%sla%', 'g'), slaBar);
    card = card.replace(new RegExp('%sla-color%', 'g'), slaColor);

    color = 'blue';

    for(var x = 0; x < upvoteData.length; x++) {
        if(upvoteData[x].uuid == uuid) {
            if(upvoteData[x].user == user.email) {
                color = 'gold';
                break;
            }
        }
    }

    card = card.replace(new RegExp('%feedback-color%', 'g'), color);

    color = 'blue';

    for(var x = 0; x < responseUpvotes.length; x++) {
        if(responseUpvotes[x].uuid == uuid) {
            if(responseUpvotes[x].user == user.email) {
                color = 'gold';
                break;
            }
        }
    }

    card = card.replace(new RegExp('%response-color%', 'g'), color);

    color = 'darkgray';
    for(var x = 0; x < flagData.length; x++) {
        if(flagData[x].uuid == uuid) {
            if(flagData[x].user == user.email) {
                color = 'red';
                break;
            }
        }
    }
    card = card.replace(new RegExp('%flag-color%', 'g'), color);

    return card
}

function showCards() {
    str = '';
    for (var x = 0; x < queueData.length; x++) {
        queueData[x].upvotes = totalFeedbackUpvotes(queueData[x].uuid);
        queueData[x].upvotes2 = totalResponseUpvotes(queueData[x].uuid);

        str += createCard(queueData[x].uuid, queueData[x].created, queueData[x].queue, queueData[x].feedback, queueData[x].response, x, queueData[x].upvotes, queueData[x].upvotes2, queueData[x].level, queueData[x].inquirer, queueData[x].updated, queueData[x].response_uuid);
    }

    document.getElementById('feedback-view-content').innerHTML = str;
}

function provideSuggestions(query) {
    arr = query.split(new RegExp(' ', 'g'));
    str = ''
    uuids = [];
    uncommon = [];

    for(var a = 0; a < arr.length; a++) {
        incomplete = false;
        word = arr[a].toLowerCase().replace(/[^\w\s]/gi, '')
        for(var b = 0; b < common.length; b++) {
            if(word == common[b]) {
                incomplete = true;
            } else if(word == '') {
                incomplete = true;
            } else if(word.length < 3) {
                incomplete = true;
            }
        }

        if(!incomplete) {
            uncommon.push(word.toLowerCase());
        }
    }

    channels = [];

    for(var y = 0; y < uncommon.length; y++) {
        word = uncommon[y].toLowerCase();

        // Match possible channels
        for(var x = 0; x < channelRef.rendell.length; x++) {
            if(channelRef.rendell[x] == word) {
                channels.push('Rendell\'s Website');
            }
        }

        // Get queue matches
        for(var x = 0; x < queueData.length; x++) {
            response = (queueData[x].response == null) ? '' : queueData[x].response.toLowerCase();

            if(queueData[x].feedback.toLowerCase().search(word) > -1) {
                uuids.push(queueData[x].uuid);
            }
        }
    }

    uniqueChannels = [];
    $.each(channels, function(i, el){
        if($.inArray(el, uniqueChannels) === -1) uniqueChannels.push(el);
    });

    uniqueCards = [];
    $.each(uuids, function(i, el){
        if($.inArray(el, uniqueCards) === -1) uniqueCards.push(el);
    });

    for(var y = 0; y < uniqueChannels.length; y++) {
        link = '';
        desc = '';
        switch(uniqueChannels[y]) {
            case 'C360':
                link = 'http://www.rtbanzon.com';
                desc = 'Visit Rendell\'s Website!';
                break;
        }

        str += '<div class="card m-2 text-center"><div class="card-header"><a href="' + link + '" target="_blank"><h5>Feedback Channel: ' + uniqueChannels[y] + '</h5></a>' + desc + '</div></div>';
    }

    for(var y = 0; y < uniqueCards.length; y++) {
        for(var x = 0; x < queueData.length; x++) {
            if(uniqueCards[y] == queueData[x].uuid) {
                str += createCard(queueData[x].uuid, queueData[x].created, queueData[x].queue, queueData[x].feedback, queueData[x].response, x, queueData[x].upvotes, queueData[x].upvotes2, queueData[x].level, queueData[x].inquirer, queueData[x].updated, queueData[x].response_uuid);
            }
        }
    }

    document.getElementById('suggestions').innerHTML = str;
}

function pingServer() {
    payload = {
        _csrf_token: token
    };

    $.ajax({
        type: 'POST',
        url: $SCRIPT_ROOT + '/ping',
        data: JSON.stringify(payload),
        contentType: "application/json; charset=utf-8",
        success: function(data) {

        }, error: function(){
            refreshPage();
        }
    });
}

function initialize() {
    queueData.sort(function(a, b) {
        if (a.upvotes > b.upvotes) return -1;
        if (a.upvotes < b.upvotes) return 1;
        return 0;
    });

    showCards();

    window.setInterval(function() {
        if(autorefresh) {
            pingServer();
        }
    }, 2000);
}

$(document).ready(function() {
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })

    $('body').on('change', '#order-by', function() {
        e = document.getElementById('order-by');
        option = e.options[e.selectedIndex].value;

        if(option == 'Most Popular') {
            queueData.sort(function(a, b) {
                if (a.upvotes > b.upvotes) return -1;
                if (a.upvotes < b.upvotes) return 1;
                return 0;
            });
        } else if(option == 'Most Recently Asked') {
            queueData.sort(function(a, b) {
                if (new Date(a.created) < new Date(b.created)) return  1;
                if (new Date(a.created) > new Date(b.created)) return -1;
                return 0;
            });
        } else if(option == 'Most Recently Updated') {
            queueData.sort(function(a, b) {
                if (new Date(a.updated) < new Date(b.updated)) return  1;
                if (new Date(a.updated) > new Date(b.updated)) return -1;
                return 0;
            });
        }

        showCards();
    });

    $('body').on('click', '.upvote', function() {
        arr = $(this).attr('id').split('.');
        type = arr[0].split('-')[1];
        uuid = arr[1];

        action = 0;

        if(type == 'feedback') {
            color = document.getElementById('upvote-feedback.' + uuid).style.color;
            if(color == 'blue') {
                document.getElementById('upvote-feedback.' + uuid).style.color = 'gold';
                action = 1;
            } else {
                document.getElementById('upvote-feedback.' + uuid).style.color = 'blue';
            }
        } else if(type == 'response') {
            color = document.getElementById('upvote-response.' + uuid).style.color;
            if(color == 'blue') {
                document.getElementById('upvote-response.' + uuid).style.color = 'gold';
                action = 1;
            } else {
                document.getElementById('upvote-response.' + uuid).style.color = 'blue';
            }
        }

        payload = {
            _csrf_token: token,
            uuid: uuid,
            action: action,
            type: type
        };

        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/data/upvote',
            data: JSON.stringify(payload),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                upvoteData = data.upvotes;
                responseUpvotes = data.upvotes2;

                if(type == 'feedback') {
                    document.getElementById('count-' + type + '.' + uuid).innerHTML = totalFeedbackUpvotes(uuid);
                } else if (type == 'response') {
                    document.getElementById('count-' + type + '.' + uuid).innerHTML = totalResponseUpvotes(uuid);   
                }
            }, error: function(){
                refreshPage();
            }
        });
    });

    $('body').on('click', '.flag-response', function() {
        uuid = $(this).attr('id').split('.')[1];

        action = 0;

        color = document.getElementById('flag-response.' + uuid).style.color;
        if(color == 'darkgray') {
            document.getElementById('flag-response.' + uuid).style.color = 'red';
            action = 1;
        } else {
            document.getElementById('flag-response.' + uuid).style.color = 'darkgray';
        }

        payload = {
            _csrf_token: token,
            uuid: uuid,
            action: action
        };

        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/data/flag',
            data: JSON.stringify(payload),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                flagData = data.flags;

                if(action == 1) {
                    Notify('Response has been flagged for review. Thanks!', null, null, 'success');
                }
            }, error: function(){
                refreshPage();
            }
        });
    });

    $('body').on('click', '.submission', function() {
        feedback = document.getElementById('askFeedback').value;

        e = document.getElementById('assignQueue');
        queue = e.options[e.selectedIndex].value;

        identify = false;

        if(document.getElementById('identify').checked) {
            identify = true;
        }

        payload = {
            _csrf_token: token,
            feedback: feedback,
            queue: queue,
            identify: identify
        };

        $('#horn1').addClass('ld');
        $('#horn1').addClass('ld-surprise');
        $('#horn2').addClass('ld');
        $('#horn2').addClass('ld-surprise');

        setTimeout(function() {
            $('#horn1').removeClass('ld');
            $('#horn1').removeClass('ld-surprise');
            $('#horn2').removeClass('ld');
            $('#horn2').removeClass('ld-surprise');
        }, 2000);

        document.getElementById('identify').checked = false;

        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/feedback',
            data: JSON.stringify(payload),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                Notify('Feedback submitted! Thanks!', null, null, 'success');
            }, error: function(){
                refreshPage();
            }
        });

        document.getElementById('askFeedback').value = '';
    });

    $('#search').keypress(function(event){
        if (event.keyCode === 10 || event.keyCode === 13) 
            event.preventDefault();
      });

    $('#search').on('keyup', function(e) {
        if(e.keyCode !== 13) {
            query = document.getElementById('search').value.toLowerCase();
            e = document.getElementById('queue-filter');
            queue = e.options[e.selectedIndex].value;

            for(var x = 0; x < queueData.length; x++) {
                response = (queueData[x].response == null) ? '' : queueData[x].response.toLowerCase();

                if((queueData[x].feedback.toLowerCase().search(query) > -1 || response.search(query) > -1) && (queueData[x].queue == queue || queue == '(All)')) {
                    document.getElementById('card' + x).style.display = 'block';
                } else {
                    document.getElementById('card' + x).style.display = 'none';
                }
            }
        }
    });

    $('#askFeedback').on('keyup', function(e) {
        query = document.getElementById('askFeedback').value.toLowerCase();

        provideSuggestions(query);
    });

    $('body').on('change', '#queue-filter', function() {
        e = document.getElementById('queue-filter');
        queue = e.options[e.selectedIndex].value;

        for(var x = 0; x < queueData.length; x++) {
            if(queueData[x].queue == queue || queue == '(All)') {
                document.getElementById('card' + x).style.display = 'block';
            } else {
                document.getElementById('card' + x).style.display = 'none';
            }
        }
    });

    $('body').on('click', '#submission-nav', function() {
        document.getElementById('submission-view').style.display = 'block';
        document.getElementById('feedback-view').style.display = 'none';

        if(notViewedGuidelines) {
            //$('#guidelines-modal').modal('toggle');
            notViewedGuidelines = false;
        }
    });

    $('body').on('click', '#feedback-nav', function() {
        document.getElementById('submission-view').style.display = 'none';
        document.getElementById('feedback-view').style.display = 'block';
    });
});