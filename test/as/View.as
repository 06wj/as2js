package com.finegamedesign.change
{
    import flash.display.Bitmap;
    import flash.display.BitmapData;
    import flash.display.DisplayObject;
    import flash.display.DisplayObjectContainer;
    import flash.display.MovieClip;
    import flash.display.Sprite;
    import flash.geom.Matrix;
    import flash.geom.Point;
    import flash.geom.Rectangle;
    import flash.events.MouseEvent;

    public class View
    {


        public static function remove(child)
        {
            if (null != child && null != child.parent && child.parent.contains(child)) {
                child.parent.removeChild(child);
            }
        }

        public static function removeAll(parent)
        {
            for (var c = parent.numChildren - 1; 0 <= c; c--) {
                View.remove(parent.getChildAt(c));
            }
        }
        public var feedbackClip;
        public var model = null;
        public var screen = null;
        public var backgroundClip;
        public var reviewClip;
        public var rounds;
        public var filterCorrect;
        public var filterWrong;



        /**
         * Hide 2nd and 3rd rounds.
         */ 
        public function View(parent = undefined)
        {
            this.feedbackClip = new FeedbackClip();
            this.screen = new Screen();
            this.rounds = this.parseRounds();
            this.backgroundClip = new BackgroundClip();
            parent.addChild(backgroundClip);
            this.backgroundClip.gotoAndPlay("begin");
            parent.addChild(screen);
            this.screen.gotoAndStop(1);
            this.screen.night.mouseChildren = false;
            this.screen.night.mouseEnabled = false;
            this.filterCorrect = new FilterCorrect().getChildAt(0).filters[0];
            this.filterWrong = new FilterWrong().getChildAt(0).filters[0];
        }



        /**
         * name_round.  Example:  TreeLeaves_0, TreeLeaves_1.
         */
        public function parseRounds()
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
                        trace("View.parseRound: " + name + " round " + r);
                    }
                }
            }
            return rounds;
        }

        public function getProperty(items = undefined, prop = undefined)
        {
            var props = [];
            for (var i = 0; i < items.length; i++) {
                props.push(items[i][prop]);
            }
            return props;
        }



        /**
         * @return Index of MovieClip in screen.rounds.
         */
        public function indexOf(stageX = undefined, stageY = undefined)
        {
            var debugHit = false;
            var point = new Point(stageX, stageY);
            var hits = this.screen.rounds.getObjectsUnderPoint(point);
            var found;
            if (debugHit) {
                trace("View.indexOf: " + hits);
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
                trace("found: " + found.name);
            }
            var index = -1;
            for (var r = 0; r < this.rounds.length; r++) {
                index = this.rounds[r].indexOf(found);
                if (0 <= index) {
                    break;
                }
            }
            return index;
        }

        public function end()
        {
            this.backgroundClip.gotoAndPlay("end");
            this.screen.addFrameScript(screen.totalFrames - 1, this.screen.stop);
        }

        public function hideScreen()
        {
            // trace("View.hideScreen");
            if (reviewClip) {
                remove(reviewClip);
                this.reviewClip.visible = false;
            }
            this.screen.stop();
            this.screen.visible = false;
            remove(screen);
        }

        public function populate(model = undefined)
        {
            this.model = this.model;
            for (var r = 0; r < this.rounds.length; r++) {
                for (var c = 0; c < this.rounds[r].length; c++) {
                    this.rounds[r][c].filters = [];
                }
            }
            if (!model.complete) {
                var previous = this.rounds[model.round][model.target];
                previous.visible = false;
                var current = this.rounds[model.round + 1][model.target];
                current.visible = true;
                if (model.trial < this.model.trialTutor) {
                    current.filters = [filterCorrect.clone()];
                    current.filters[0].strength = 6.0 - 0.05 * this.model.referee.percent;
                }
            }
        }

        public function review()
        {
            trace("View.review");
            this.screen.stop();
            this.reviewClip = new ReviewClip();
            this.screen.addChild(reviewClip);
            this.reviewClip.addFrameScript(reviewClip.totalFrames - 3, this.screen.play);
            this.screen.rounds.alpha = 0.0;
            this.reviewClip.count.text = this.model.referee.percent.toString() + "%";
            this.reviewClip.minutes.text = this.model.referee.minutes;
            this.reviewClip.score.text = this.model.referee.score.toString();
            this.reviewClip.count.mouseEnabled = false;
            this.reviewClip.minutes.mouseEnabled = false;
        }

        public function win()
        {
            if ("trial" != this.backgroundClip.currentLabel) {
                this.backgroundClip.gotoAndPlay("trial");
            }
        }

        public function feedback(targetIndex = undefined, correct = undefined)
        {
            var target = this.rounds[model.round][targetIndex];
            this.feedbackClip.x = target.x;
            this.feedbackClip.y = target.y;
            target.parent.addChild(feedbackClip);
            var label = correct ? "correct" : "wrong";
            this.feedbackClip.gotoAndPlay(label);
            target.filters = correct ? [filterCorrect.clone()]
                                        : [filterWrong.clone()];
        }

        public function cancel()
        {
        }

        public function trialEnd()
        {
            this.cancel();
            if ("end" != this.screen.currentLabel) {
                this.screen.gotoAndPlay("end");
            }
        }

        public function clear()
        {
            this.cancel();
        }

        public function restart()
        {
            this.hideScreen();
            this.clear();
            this.backgroundClip.stop();
            this.screen.stop();
            remove(backgroundClip);
        }
    }
}