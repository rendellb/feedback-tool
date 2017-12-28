var queueData = data.queue;
var upvoteData = data.upvotes;
var openData = data.open;
var modData = data.mod;
var reviewData = data.review;
var amendData = data.amend;
var flagData = data.flags;
var autorefresh = true;

function refreshPage() {
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

function addUpvotesAndSort() {
    for(var x = 0; x < queueData.length; x++) {
        queueData[x].upvotes = 0;
        for(var y = 0; y < upvoteData.length; y++) {
            if(upvoteData[y].uuid == queueData[x].uuid) {
                queueData[x].upvotes += 1;
            }
        }
    }

    queueData.sort(function(a, b) {
        if (a.upvotes < b.upvotes) {
            return 1;
        }

        if (a.upvotes > b.upvotes) {
            return -1;
        }

        return 0;
    });

    for(var x = 0; x < amendData.length; x++) {
        amendData[x].flags = 0;
        for(var y = 0; y < flagData.length; y++) {
            if(flagData[y].uuid == amendData[x].response_uuid) {
                amendData[x].flags += 1;
            }
        }
    }

    amendData.sort(function(a, b) {
        if (a.flags < b.flags) {
            return 1;
        }

        if (a.flags > b.flags) {
            return -1;
        }

        return 0;
    });
}

function checkClear(query) {
    if(query !== '' && query !== undefined && query !== null) {
        return true;    
    } else {
        return false;    
    }
}

function queueCard(uuid, created, queue, level, feedback, upvotes, claim, notes, response, ruuid, deescalated) {
    card = $('#main-card').html().toString();

    if(claim == user.email) {
        card = card.replace('%claim-button%', '');
    } else {
        card = card.replace('%claim-button%', '<button class="btn btn-outline-info m-1 w-100 claim" id="claim.' + uuid + '" type="button">Claim</button>');
    }

    deescalateButton = '';

    if(level > 2) {
        deescalateButton = '<button class="btn btn-outline-success m-1 w-100 deescalate" id="deescalate.' + uuid + '" type="button">De-escalate</button>';
    }

    card = card.replace('%deescalate-button%', deescalateButton);

    card = card.replace('%created%', created);
    card = card.replace('%queue%', queue);
    card = card.replace('%feedback%', feedback);
    card = card.replace('%upvotes%', upvotes);
    card = card.replace(new RegExp('%uuid%', 'g'), uuid);
    card = card.replace(new RegExp('%level%', 'g'), 'L' + level);

    responseStr = ''
    responseUUID = ''
    notesStr = '';
    escalateButton = '';
    if(checkClear(response)) {
        responseStr = response;
        responseUUID = ruuid;
        notesStr = '<div>Response Rejected by Manager: ' + notes + '</div>';
    } else if(!checkClear(deescalated) && level < 4) {
        escalateButton = '<button class="btn btn-outline-danger m-1 w-100 escalate" id="escalate.' + uuid + '" type="button">Escalate</button>';
    }

    card = card.replace('%escalate-button%', escalateButton);

    card = card.replace(new RegExp('%ruuid%', 'g'), responseUUID);
    card = card.replace('%response%', responseStr);
    card = card.replace('%notes%', notesStr);

    return card
}

function openCard(uuid, created, queue, level, feedback, upvotes, claim, notes, response, ruuid) {
    card = $('#open-card').html().toString();

    card = card.replace('%claim-button%', '<button class="btn btn-outline-info m-1 w-100 claim" id="claim.' + uuid + '" type="button">Claim</button>');

    card = card.replace('%created%', created);
    card = card.replace('%queue%', queue);
    card = card.replace('%feedback%', feedback);
    card = card.replace('%upvotes%', upvotes);
    card = card.replace(new RegExp('%uuid%', 'g'), uuid);
    card = card.replace(new RegExp('%level%', 'g'), 'L' + level);

    return card
}

function reviewCard(uuid, created, queue, level, feedback, response, upvotes, response_uuid, assignee) {
    card = $('#review-card').html().toString();

    card = card.replace('%created%', created);
    card = card.replace('%queue%', queue);
    card = card.replace('%feedback%', feedback);
    card = card.replace('%response%', response);
    card = card.replace('%upvotes%', upvotes);
    card = card.replace(new RegExp('%uuid%', 'g'), uuid);
    card = card.replace(new RegExp('%response-uuid%', 'g'), response_uuid);
    card = card.replace(new RegExp('%assignee%', 'g'), assignee);

    return card
}

function amendCard(uuid, created, queue, level, feedback, response, flags, response_uuid, assignee, correct) {
    card = $('#amend-card').html().toString();

    markCorrect = '';
    color = '#a2d9ce';
    correction = '';

    if(flags > 12) {
        if(correct !== '') {
            markCorrect = '<br /><br /><div style="color: green;">Response was marked correct by ' + correct + '.</div>';
        } else {
            color = '#ffaaaa';
            markCorrect = '<button class="btn btn-outline-success m-1 w-100 correct" id="correct.' + response_uuid + '" type="button">Mark as Correct</button>';
        }
    }

    card = card.replace('%created%', created);
    card = card.replace('%queue%', queue);
    card = card.replace('%feedback%', feedback);
    card = card.replace('%response%', response);
    card = card.replace('%flags%', flags);
    card = card.replace(new RegExp('%uuid%', 'g'), uuid);
    card = card.replace(new RegExp('%response-uuid%', 'g'), response_uuid);
    card = card.replace(new RegExp('%level%', 'g'), 'L' + level);
    card = card.replace(new RegExp('%flag-color%', 'g'), color);
    card = card.replace(new RegExp('%mark-correct%', 'g'), markCorrect);
    card = card.replace(new RegExp('%ruuid%', 'g'), response_uuid);

    return card
}

function modCard(uuid, feedback) {
    card = $('#mod-card').html().toString();

    card = card.replace('%feedback%', feedback);
    card = card.replace(new RegExp('%uuid%', 'g'), uuid);

    return card
}

function checkEmptyQueues() {
    /* if(queueData.length < 1) {
        document.getElementById('assignments').innerHTML = 'No assignments.';    
    } */
}

function makeQueues() {
    addUpvotesAndSort();

    assignments = '';
    for (var x = 0; x < queueData.length; x++) {
        assignments += queueCard(queueData[x].uuid, queueData[x].created, queueData[x].queue, queueData[x].level, queueData[x].feedback, queueData[x].upvotes, queueData[x].claim, queueData[x].notes, queueData[x].response, queueData[x].response_uuid, queueData[x].deescalated);
    }
    document.getElementById('assignments').innerHTML = assignments;

    makeOpenQueue();

    makeReviewQueue();

    amend = '';
    for (var x = 0; x < amendData.length; x++) {
        amend += amendCard(amendData[x].uuid, amendData[x].created, amendData[x].queue, amendData[x].level, amendData[x].feedback, amendData[x].response, amendData[x].flags, amendData[x].response_uuid, amendData[x].assignee, amendData[x].correct);
    }
    document.getElementById('amend').innerHTML = amend;

    makeModQueue();

    checkEmptyQueues();
}

function makeOpenQueue() {
    queueData.sort(function(a, b) {
        if (a.upvotes < b.upvotes) {
            return 1;
        }

        if (a.upvotes > b.upvotes) {
            return -1;
        }

        return 0;
    });

    for(var x = 0; x < openData.length; x++) {
        openData[x].upvotes = 0;
        for(var y = 0; y < upvoteData.length; y++) {
            if(upvoteData[y].uuid == openData[x].uuid) {
                openData[x].upvotes += 1;
            }
        }
    }

    queue = '';
    for (var x = 0; x < openData.length; x++) {
        queue += openCard(openData[x].uuid, openData[x].created, openData[x].queue, openData[x].level, openData[x].feedback, openData[x].upvotes, openData[x].claim);
    }
    document.getElementById('queue').innerHTML = queue;    
}

function makeReviewQueue() {
    for(var x = 0; x < reviewData.length; x++) {
        reviewData[x].upvotes = 0;
        for(var y = 0; y < upvoteData.length; y++) {
            if(upvoteData[y].uuid == reviewData[x].uuid) {
                reviewData[x].upvotes += 1;
            }
        }
    }

    reviewData.sort(function(a, b) {
        if (a.upvotes < b.upvotes) {
            return 1;
        }

        if (a.upvotes > b.upvotes) {
            return -1;
        }

        return 0;
    });

    review = '';
    for (var x = 0; x < reviewData.length; x++) {
        review += reviewCard(reviewData[x].uuid, reviewData[x].created, reviewData[x].queue, reviewData[x].level, reviewData[x].feedback, reviewData[x].response, reviewData[x].upvotes, reviewData[x].response_uuid, reviewData[x].assignee);
    }
    document.getElementById('review').innerHTML = review;    
}

function makeModQueue() {
    mods = '';
    for (var x = 0; x < modData.length; x++) {
        mods += modCard(modData[x].uuid, modData[x].feedback);
    }
    document.getElementById('mod').innerHTML = mods;
}

function saveReview(ruuid, confirm, comments) {
    fuuid = document.getElementById('response.' + ruuid).parentNode.parentNode.parentNode.id.split('.')[1];
    assignee = document.getElementById('assignee.' + ruuid).innerHTML;

    payload = {
        _csrf_token: token,
        fuuid: fuuid,
        ruuid: ruuid,
        confirm: confirm,
        comments: comments,
        assignee: assignee
    };

    $.ajax({
        type: 'POST',
        url: $SCRIPT_ROOT + '/data/review',
        data: JSON.stringify(payload),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            document.getElementById('card.' + fuuid).style.display = 'none';
            Notify('Review saved!', null, null, 'success');
        }, error: function(){
            refreshPage();
        }
    });   
}

function checkNewFeedback() {
    $.ajax({
        type: 'GET',
        url: $SCRIPT_ROOT + '/data/queue',
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            newQueue = data.queue;
            newReview = data.review;
            openData = data.open;
            modData = data.mod;

            for(var x = 0; x < newQueue.length; x++) {
                uuidNotFound = true;
                for(var y = 0; y < queueData.length; y++) {
                    if(newQueue[x].uuid == queueData[y].uuid) {
                        uuidNotFound = false;

                        if(newQueue[x].claim !== null && newQueue[x].claim !== '') {
                            if(newQueue[x].claim !== user.email) {
                                document.getElementById('card.' + newQueue[x].uuid).style.display = 'none';
                            }
                        }

                        break;
                    }
                }

                if(uuidNotFound) {
                    $('#assignments').append(queueCard(newQueue[x].uuid, newQueue[x].created, newQueue[x].queue, newQueue[x].level, newQueue[x].feedback, 0, newQueue[x].claim, newQueue[x].notes, newQueue[x].response, newQueue[x].response_uuid, newQueue[x].deescalated));
                }
            }

            for(var x = 0; x < newReview.length; x++) {
                uuidNotFound = true;
                for(var y = 0; y < reviewData.length; y++) {
                    if(newReview[x].uuid == reviewData[y].uuid) {
                        uuidNotFound = false;

                        if(newReview[x].claim !== null && newReview[x].claim !== '') {
                            if(newReview[x].claim !== user.email) {
                                document.getElementById('card.' + newReview[x].uuid).style.display = 'none';
                            }
                        }

                        break;
                    }
                }

                if(uuidNotFound) {
                    $('#review').append(reviewCard(newReview[x].uuid, newReview[x].created, newReview[x].queue, newReview[x].level, newReview[x].feedback, 0, newReview[x].claim, newReview[x].notes, newReview[x].response, newReview[x].response_uuid, newReview[x].assignee));
                }
            }

            queueData = newQueue;
            reviewData = newReview;

            makeReviewQueue();
            makeModQueue();
            makeOpenQueue();
            updateCounters();
            checkEmptyQueues();
        }, error: function(){
            refreshPage();
        }
    });
}

function updateCounters() {
    if(queueData.length > 0) {
        document.getElementById('assignment-count').innerHTML = '(' + queueData.length + ')';
        document.getElementById('assignment-count').style.color = 'lightblue';
    } else {
        document.getElementById('assignment-count').innerHTML = '';
    }

    if(openData.length > 0) {
        document.getElementById('open-count').innerHTML = '(' + openData.length + ')';
        document.getElementById('open-count').style.color = 'lightblue';
    } else {
        document.getElementById('open-count').innerHTML = '';
    }

    if(modData.length > 0) {
        document.getElementById('mod-count').innerHTML = '(' + modData.length + ')';
        document.getElementById('mod-count').style.color = 'lightblue';
    } else {
        document.getElementById('mod-count').innerHTML = '';
    }

    if(reviewData.length > 0) {
        document.getElementById('review-count').innerHTML = '(' + reviewData.length + ')';
        document.getElementById('review-count').style.color = 'lightblue';
    } else {
        document.getElementById('review-count').innerHTML = '';
    }
}

function initialize() {
    makeQueues();
    updateCounters();

    if(user.level < 3) {
        document.getElementById('review-nav').style.display = 'none';   
        document.getElementById('amend-nav').style.display = 'none';   
        document.getElementById('mod-nav').style.display = 'none';   
    }

    window.setInterval(function() {
        if(autorefresh) {
            checkNewFeedback();
        }
    }, 2000);
}

$(document).ready(function() {
    $('body').on('click', '.view-change', function() {
        view = $(this).attr('id');

        if(view == 'assignment-nav') {
            document.getElementById('assignment-view').style.display = 'block';
            document.getElementById('queue-view').style.display = 'none';
            document.getElementById('review-view').style.display = 'none';
            document.getElementById('amend-view').style.display = 'none';
            document.getElementById('mod-view').style.display = 'none';
        } else if(view == 'open-nav') {
            document.getElementById('assignment-view').style.display = 'none';
            document.getElementById('queue-view').style.display = 'block';
            document.getElementById('review-view').style.display = 'none';
            document.getElementById('amend-view').style.display = 'none';
            document.getElementById('mod-view').style.display = 'none';
        } else if(view == 'review-nav') {
            document.getElementById('assignment-view').style.display = 'none';
            document.getElementById('queue-view').style.display = 'none';
            document.getElementById('review-view').style.display = 'block';
            document.getElementById('amend-view').style.display = 'none';
            document.getElementById('mod-view').style.display = 'none';
        } else if(view == 'amend-nav') {
            document.getElementById('assignment-view').style.display = 'none';
            document.getElementById('queue-view').style.display = 'none';
            document.getElementById('review-view').style.display = 'none';
            document.getElementById('amend-view').style.display = 'block';
            document.getElementById('mod-view').style.display = 'none';
        } else if(view == 'mod-nav') {
            document.getElementById('assignment-view').style.display = 'none';
            document.getElementById('queue-view').style.display = 'none';
            document.getElementById('review-view').style.display = 'none';
            document.getElementById('amend-view').style.display = 'none';
            document.getElementById('mod-view').style.display = 'block';
        }
    });

    $('body').on('click', '.claim', function() {
        uuid = $(this).attr('id').split('.')[1];

        try {
            document.getElementById('open.' + uuid).style.display = 'none';
        } catch(err) {}

        payload = {
            _csrf_token: token,
            uuid: uuid
        };

        Notify('Claiming.' + uuid, null, null, 'warning');
        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/data/claim',
            data: JSON.stringify(payload),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                Notify('Claimed: ' + uuid, null, null, 'success');
                document.getElementById('claim.' + uuid).style.display = 'none';
            }, error: function(){
                refreshPage();
            }
        });
    });

    $('body').on('click', '.escalate', function() {
        uuid = $(this).attr('id').split('.')[1];
        document.getElementById($(this).attr('id')).disabled = true;

        payload = {
            _csrf_token: token,
            uuid: uuid,
            user: user.email
        };

        Notify('Escalating.', null, null, 'warning');
        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/data/escalate',
            data: JSON.stringify(payload),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                Notify('Escalated: ' + uuid, null, null, 'success');
                queueData = data.results;

                foundFeedback = false;
                for(var x = 0; x < queueData.length; x++) {
                    if(queueData[x].uuid == uuid) {
                        foundFeedback = true;    
                    }
                }

                if(!foundFeedback) {
                    document.getElementById('card.' + uuid).style.display = 'none';
                }
            }, error: function(){
                refreshPage();
            }
        });
    });

    $('body').on('click', '.deescalate', function() {
        uuid = $(this).attr('id').split('.')[1];
        document.getElementById($(this).attr('id')).disabled = true;

        payload = {
            _csrf_token: token,
            uuid: uuid,
            user: user.email
        };

        Notify('De-escalating.', null, null, 'warning');
        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/data/deescalate',
            data: JSON.stringify(payload),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                Notify('De-escalated: ' + uuid, null, null, 'success');
                queueData = data.results;

                foundFeedback = false;
                for(var x = 0; x < queueData.length; x++) {
                    if(queueData[x].uuid == uuid) {
                        foundFeedback = true;    
                    }
                }

                if(!foundFeedback) {
                    document.getElementById('card.' + uuid).style.display = 'none';
                }
            }, error: function(){
                refreshPage();
            }
        });
    });

    $('body').on('click', '.reassign', function() {
        uuid = $(this).attr('id').split('.')[1];
        queue = $(this).html();

        payload = {
            _csrf_token: token,
            uuid: uuid,
            user: user.email,
            queue: queue
        };

        Notify('Reassigning.', null, null, 'warning');
        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/data/reassign',
            data: JSON.stringify(payload),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                Notify('Reassigned: ' + uuid, null, null, 'success');
                queueData = data.results;

                makeQueues();
            }, error: function(){
                refreshPage();
            }
        });
    });

    $('body').on('click', '.correct', function() {
        ruuid = document.getElementById($(this).attr('id')).parentNode.id;

        payload = {
            _csrf_token: token,
            ruuid: ruuid
        };

        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/data/mark-correct',
            data: JSON.stringify(payload),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                Notify('Marked Correct: ' + ruuid, null, null, 'success');
            }, error: function() {
                refreshPage();
            }
        });
    });

    $('body').on('click', '.submission', function() {
        uuid = $(this).attr('id').split('.')[1];
        response = document.getElementById('response.' + uuid).value.replace(/\n\r?/g, '<br />');
        ruuid = document.getElementById('submit.' + uuid).parentNode.id;

        if(ruuid == '') {
            payload = {
                _csrf_token: token,
                uuid: uuid,
                response: response
            };

            Notify('Submitting.', null, null, 'warning');
            $.ajax({
                type: 'POST',
                url: $SCRIPT_ROOT + '/data/submit',
                data: JSON.stringify(payload),
                contentType: "application/json; charset=utf-8",
                success: function(data) {
                    Notify('Submitted: ' + uuid, null, null, 'success');
                    queueData = data.results;

                    foundFeedback = false;
                    for(var x = 0; x < queueData.length; x++) {
                        if(queueData[x].uuid == uuid) {
                            foundFeedback = true;    
                        }
                    }

                    if(!foundFeedback) {
                        document.getElementById('card.' + uuid).style.display = 'none';
                    }
                }, error: function(){
                    refreshPage();
                }
            });
        } else {
            payload = {
                _csrf_token: token,
                uuid: uuid,
                ruuid: ruuid,
                response: response
            };

            Notify('Submitting.', null, null, 'warning');
            $.ajax({
                type: 'POST',
                url: $SCRIPT_ROOT + '/data/submitcorrection',
                data: JSON.stringify(payload),
                contentType: "application/json; charset=utf-8",
                success: function(data) {
                    Notify('Submitted: ' + uuid, null, null, 'success');
                    queueData = data.results;

                    foundFeedback = false;
                    for(var x = 0; x < queueData.length; x++) {
                        if(queueData[x].uuid == uuid) {
                            foundFeedback = true;    
                        }
                    }

                    if(!foundFeedback) {
                        document.getElementById('card.' + uuid).style.display = 'none';
                    }
                }, error: function() {
                    refreshPage();
                }
            });
        }
    });

    $('body').on('click', '.amendment', function() {
        uuid = $(this).attr('id').split('.')[1];
        response = document.getElementById('response.' + uuid).value.replace(/\n\r?/g, '<br />');

        payload = {
            _csrf_token: token,
            uuid: uuid,
            response: response
        };

        Notify('Submitting.', null, null, 'warning');
        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/data/amend',
            data: JSON.stringify(payload),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                Notify('Submitted: ' + uuid, null, null, 'success');
                queueData = data.results;

                foundFeedback = false;
                for(var x = 0; x < queueData.length; x++) {
                    if(queueData[x].uuid == uuid) {
                        foundFeedback = true;
                    }
                }

                if(!foundFeedback) {
                    document.getElementById('card.' + uuid).style.display = 'none';
                }
            }, error: function(){
                refreshPage();
            }
        });
    });

    $('body').on('click', '.edit', function() {
        uuid = $(this).attr('id').split('.')[1];

        if(document.getElementById('edit.' + uuid).innerText == 'Edit') {
            document.getElementById('response.' + uuid).disabled = false;
            document.getElementById('edit.' + uuid).innerText = 'Submit with Changes';
            document.getElementById('approved.' + uuid).innerText = 'Approve Original';
        } else {
            newResponse = document.getElementById('response.' + uuid).value;
            fuuid = document.getElementById('response.' + uuid).parentNode.parentNode.parentNode.id.split('.')[1];

            payload = {
                fuuid: fuuid,
                uuid: uuid,
                response: newResponse
            }

            $.ajax({
                type: 'POST',
                url: $SCRIPT_ROOT + '/data/edit-submit',
                data: JSON.stringify(payload),
                contentType: "application/json; charset=utf-8",
                success: function(data) {
                    document.getElementById('card.' + fuuid).style.display = 'none';
                    Notify('Edited response submitted!', null, null, 'success');
                }, error: function(){
                    refreshPage();
                }
            });
        }
    });

    $('body').on('click', '.review', function() {
        arr = $(this).attr('id').split('.');
        confirm = arr[0];
        ruuid = arr[1];
        comments = '';
        if(confirm == 'denied') {
            comments = document.getElementById('denial-comments').value;
        }

        saveReview(ruuid, confirm, comments);
    });

    $('body').on('click', '.deny', function() {
        arr = $(this).attr('id').split('.');
        uuid = arr[1];

        document.getElementById('denyButton').innerHTML = '<button class="btn btn-primary m-1 w-100 review" id="denied.' + uuid + '" type="button" data-toggle="modal" data-target="#denyModal">Deny with Comments</button>';
    });

    $('body').on('click', '.verify', function() {
        answer = $(this).attr('id').split('.')[0];
        uuid = $(this).attr('id').split('.')[1];

        verify = 0;

        if(answer == 'yes') {
            verify = 1;    
        } else if(answer == 'no') {
            verify = 2;    
        }

        payload = {
            _csrf_token: token,
            uuid: uuid,
            user: user.email,
            verify: verify
        };

        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/data/modverify',
            data: JSON.stringify(payload),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                modData = data.mod;

                makeQueues();
            }, error: function(){
                refreshPage();
            }
        });
    });
});