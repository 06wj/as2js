var View = cc.Class.extend({
    feedbackClip: undefined,
    model: undefined,
    screen: undefined,
    backgroundClip: undefined,
    reviewClip: undefined,
    rounds: undefined,
    filterCorrect: undefined,
    filterWrong: undefined,



    /**
     * Hide 2nd and 3rd rounds.
     */ 
    ctor: function(parent)
    {
        feedbackClip = new FeedbackClip();
        screen = new Screen();
        rounds = parseRounds();
        backgroundClip = new BackgroundClip();
        parent.addChild(backgroundClip);
        backgroundClip.gotoAndPlay("begin");
        parent.addChild(screen);
        screen.gotoAndStop(1);
        screen.night.mouseChildren = false;
        screen.night.mouseEnabled = false;
        filterCorrect = new FilterCorrect().getChildAt(0).filters[0];
        filterWrong = new FilterWrong().getChildAt(0).filters[0];
    },



    /**
     * name_round.  Example:  TreeLeaves_0, TreeLeaves_1.
     */
    parseRounds: function()
    {
        var rounds = [];
        var max = 0;
        var r;
        var parent = screen.rounds;
        for (var c = 0; c < parent.numChildren; c++) {
            var child = parent.getChildAt(c) as MovieClip;
            if (child) {
                var names = child.name.split("_");
                if (2 <= names.length) {
                    r = parseInt(names[1]);
                    max = Math.max(max, r);
                    if (1 <= r) {
                        child.visible = false;
                    }
                    if (rounds[r] == null) {
                        rounds[r] = [];
                    }
                    rounds[r].push(child);
                }
            }
        }
        for (r = 0; r <= max; r++) {
            rounds[r].sortOn("name");
            if (1 <= r) {
                if (rounds[r].length != rounds[0].length) {
                    var names0 = getProperty(rounds[0], "name")
                    var namesR = getProperty(rounds[r], "name")
                    throw new Error("Expected same number of items in each round.");
                }
                for (c = 0; c < rounds[r].length; c++) {
                    var name0 = rounds[0][c].name.split("_")[0];
                    var name = rounds[r][c].name.split("_")[0];
                    if (name != name0) {
                        throw new Error("Expected name prefixes same.");
                    }
                    trace("View.parseRound: " + name + " round " + r);
                }
            }
        }
        return rounds;
    },

    getProperty: function(items, prop)
    {
        var props = [];
        for (var i = 0; i < items.length; i++) {
            props.push(items[i][prop]);
        }
        return props;
    },



    /**
     * @return Index of MovieClip in screen.rounds.
     */
    indexOf: function(stageX, stageY)
    {
        var debugHit = false;
        var point = new Point(stageX, stageY);
        var hits = screen.rounds.getObjectsUnderPoint(point);
        var found;
        if (debugHit) {
            trace("View.indexOf: " + hits);
        }
        for (var h = hits.length - 1; 0 <= h; h--) {
            found = null;
            var hit = hits[h];
            if (hit is MovieClip varvar screen.rounds != hit) {
                found = hit as MovieClip;
            }
            else if (hit.parent varvar hit.parent is MovieClip varvar screen.rounds != hit.parent) {
                found = hit.parent;
            }
            if (found) {
                var bmp = new BitmapData(found.width, found.height, true, 0x00000000);
                var matrix = new Matrix();
                var rect = found.getRect(found);
                matrix.translate(-rect.x, -rect.y);
                bmp.draw(found, matrix);
                var p = new Point(stageX, stageY);
                p = found.globalToLocal(p);
                p.x -= rect.left;
                p.y -= rect.top;
                var pixel = bmp.getPixel32(p.x, p.y);
                if (debugHit) { 
                    var bm = new Bitmap(bmp);
                    screen.addChild(bm);
                    if (found) {
                        trace("    name: " + found.name + " point " + p 
                            + " rect " + rect + " pixel " + pixel.toString(16));
                    }
                    var color = 0x0000FF;
                    if (!pixel) {
                        found = null;
                        color = 0xFF0000;
                    }
                    var sprite = new Sprite();
                    sprite.graphics.beginFill(color);
                    sprite.graphics.drawCircle(p.x, p.y, 10);
                    sprite.graphics.endFill();
                    screen.addChild(sprite);
                }
                if (pixel) {
                    break;
                }
                else {
                    found = null;
                }
            }
        }
        if (found) {
            trace("found: " + found.name);
        }
        var index = -1;
        for (var r = 0; r < rounds.length; r++) {
            index = rounds[r].indexOf(found);
            if (0 <= index) {
                break;
            }
        }
        return index;
    },

    end: function()
    {
        backgroundClip.gotoAndPlay("end");
        screen.addFrameScript(screen.totalFrames - 1, screen.stop);
    },

    hideScreen: function()
    {
        // trace("View.hideScreen");
        if (reviewClip) {
            remove(reviewClip);
            reviewClip.visible = false;
        }
        screen.stop();
        screen.visible = false;
        remove(screen);
    },

    populate: function(model)
    {
        this.model = model;
        for (var r = 0; r < rounds.length; r++) {
            for (var c = 0; c < rounds[r].length; c++) {
                rounds[r][c].filters = [];
            }
        }
        if (!model.complete) {
            var previous = rounds[model.round][model.target];
            previous.visible = false;
            var current = rounds[model.round + 1][model.target];
            current.visible = true;
            if (model.trial < model.trialTutor) {
                current.filters = [filterCorrect.clone()];
                current.filters[0].strength = 6.0 - 0.05 * model.referee.percent;
            }
        }
    },

    review: function()
    {
        trace("View.review");
        screen.stop();
        reviewClip = new ReviewClip();
        screen.addChild(reviewClip);
        reviewClip.addFrameScript(reviewClip.totalFrames - 3, screen.play);
        screen.rounds.alpha = 0.0;
        reviewClip.count.text = model.referee.percent.toString() + "%";
        reviewClip.minutes.text = model.referee.minutes;
        reviewClip.score.text = model.referee.score.toString();
        reviewClip.count.mouseEnabled = false;
        reviewClip.minutes.mouseEnabled = false;
    },

    win: function()
    {
        if ("trial" != backgroundClip.currentLabel) {
            backgroundClip.gotoAndPlay("trial");
        }
    },

    feedback: function(targetIndex, correct)
    {
        var target = rounds[model.round][targetIndex];
        feedbackClip.x = target.x;
        feedbackClip.y = target.y;
        target.parent.addChild(feedbackClip);
        var label = correct ? "correct" : "wrong";
        feedbackClip.gotoAndPlay(label);
        target.filters = correct ? [filterCorrect.clone()]
                                    : [filterWrong.clone()];
    },

    cancel: function()
    {
    },

    trialEnd: function()
    {
        cancel();
        if ("end" != screen.currentLabel) {
            screen.gotoAndPlay("end");
        }
    },

    clear: function()
    {
        cancel();
    },

    restart: function()
    {
        hideScreen();
        clear();
        backgroundClip.stop();
        screen.stop();
        remove(backgroundClip);
    }
});



View.remove = function(child)
{
    if (null != child varvar null != child.parent varvar child.parent.contains(child)) {
        child.parent.removeChild(child);
    }
}

View.removeAll = function(parent)
{
    for (var c = parent.numChildren - 1; 0 <= c; c--) {
        remove(parent.getChildAt(c));
    }
}