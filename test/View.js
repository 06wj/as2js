require("flash/display/Bitmap.js");
require("flash/display/BitmapData.js");
require("flash/display/DisplayObject.js");
require("flash/display/DisplayObjectContainer.js");
require("flash/display/MovieClip.js");
require("flash/display/Sprite.js");
require("flash/geom/Matrix.js");
require("flash/geom/Point.js");
require("flash/geom/Rectangle.js");
require("flash/events/MouseEvent.js");



/**
 * By Ethan Kennerly
 */
var View = cc.Class.extend({
    feedbackClip: undefined,
    model: null,
    screen: null,
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
        this.model = null;
        this.screen = null;
        this.feedbackClip = new FeedbackClip();
        this.screen = new Screen();
        this.rounds = this.parseRounds();
        this.backgroundClip = new BackgroundClip();
        parent.addChild(this.backgroundClip);
        this.backgroundClip.gotoAndPlay("begin");
        parent.addChild(this.screen);
        this.screen.gotoAndStop(1);
        this.screen.night.mouseChildren = false;
        this.screen.night.mouseEnabled = false;
        this.filterCorrect = new FilterCorrect().getChildAt(0).filters[0];
        this.filterWrong = new FilterWrong().getChildAt(0).filters[0];
    },

    /**
     * name_round.  Example:  TreeLeaves_0, TreeLeaves_1.
     */
    parseRounds: function()
    {
        var rounds = [];
        var max = 0;
        var r;
        var parent = this.screen.rounds;
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
                    var names0 = this.getProperty(rounds[0], "name")
                    var namesR = this.getProperty(rounds[r], "name")
                    throw new Error("Expected same number of items in each round.");
                }
                for (c = 0; c < rounds[r].length; c++) {
                    var name0 = rounds[0][c].name.split("_")[0];
                    var name = rounds[r][c].name.split("_")[0];
                    if (name != name0) {
                        throw new Error("Expected name prefixes same.");
                    }
                    cc.log("View.parseRound: " + name + " round " + r);
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
        var hits = this.screen.rounds.getObjectsUnderPoint(point);
        var found;
        if (debugHit) {
            cc.log("View.indexOf: " + hits);
        }
        for (var h = hits.length - 1; 0 <= h; h--) {
            found = null;
            var hit = hits[h];
            if (hit is MovieClip && this.screen.rounds != hit) {
                found = hit as MovieClip;
            }
            else if (hit.parent && hit.parent is MovieClip && this.screen.rounds != hit.parent) {
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
                    this.screen.addChild(bm);
                    if (found) {
                        cc.log("    name: " + found.name + " point " + p 
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
                    this.screen.addChild(sprite);
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
            cc.log("found: " + found.name);
        }
        var index = -1;
        for (var r = 0; r < this.rounds.length; r++) {
            index = this.rounds[r].indexOf(found);
            if (0 <= index) {
                break;
            }
        }
        return index;
    },

    end: function()
    {
        this.backgroundClip.gotoAndPlay("end");
        this.screen.addFrameScript(this.screen.totalFrames - 1, this.screen.stop);
    },

    hideScreen: function()
    {
        // cc.log("View.hideScreen");
        if (this.reviewClip) {
            View.remove(this.reviewClip);
            this.reviewClip.visible = false;
        }
        this.screen.stop();
        this.screen.visible = false;
        View.remove(this.screen);
    },

    populate: function(model)
    {
        this.model = this.model;
        for (var r = 0; r < this.rounds.length; r++) {
            for (var c = 0; c < this.rounds[r].length; c++) {
                this.rounds[r][c].filters = [];
            }
        }
        if (!this.model.complete) {
            var previous = this.rounds[this.model.round][this.model.target];
            previous.visible = false;
            var current = this.rounds[this.model.round + 1][this.model.target];
            current.visible = true;
            if (this.model.trial < this.model.trialTutor) {
                current.filters = [this.filterCorrect.clone()];
                current.filters[0].strength = 6.0 - 0.05 * this.model.referee.percent;
            }
        }
    },

    review: function()
    {
        cc.log("View.review");
        this.screen.stop();
        this.reviewClip = new ReviewClip();
        this.screen.addChild(this.reviewClip);
        this.reviewClip.addFrameScript(this.reviewClip.totalFrames - 3, this.screen.play);
        this.screen.rounds.alpha = 0.0;
        this.reviewClip.count.text = this.model.referee.percent.toString() + "%";
        this.reviewClip.minutes.text = this.model.referee.minutes;
        this.reviewClip.score.text = this.model.referee.score.toString();
        this.reviewClip.count.mouseEnabled = false;
        this.reviewClip.minutes.mouseEnabled = false;
    },

    win: function()
    {
        if ("trial" != this.backgroundClip.currentLabel) {
            this.backgroundClip.gotoAndPlay("trial");
        }
    },

    feedback: function(targetIndex, correct)
    {
        var target = this.rounds[this.model.round][targetIndex];
        this.feedbackClip.x = target.x;
        this.feedbackClip.y = target.y;
        target.parent.addChild(this.feedbackClip);
        var label = correct ? "correct" : "wrong";
        this.feedbackClip.gotoAndPlay(label);
        target.filters = correct ? [this.filterCorrect.clone()]
                                    : [this.filterWrong.clone()];
    },

    cancel: function()
    {
    },

    trialEnd: function()
    {
        this.cancel();
        if ("end" != this.screen.currentLabel) {
            this.screen.gotoAndPlay("end");
        }
    },

    clear: function()
    {
        this.cancel();
    },

    restart: function()
    {
        this.hideScreen();
        this.clear();
        this.backgroundClip.stop();
        this.screen.stop();
        View.remove(this.backgroundClip);
    }
});



View.remove = function(child)
{
    if (null != child && null != child.parent && child.parent.contains(child)) {
        child.parent.removeChild(child);
    }
}

View.removeAll = function(parent)
{
    for (var c = parent.numChildren - 1; 0 <= c; c--) {
        View.remove(parent.getChildAt(c));
    }
}