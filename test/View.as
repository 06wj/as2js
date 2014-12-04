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

    /**
     * By Ethan Kennerly
     */
    public class View
    {
        internal var feedbackClip:MovieClip;
        internal var model:Model;
        internal var screen:Screen;
        internal var backgroundClip:BackgroundClip;
        private var reviewClip:ReviewClip;
        internal var rounds:Array;
        private var filterCorrect:*;
        private var filterWrong:*;

        /**
         * Hide 2nd and 3rd rounds.
         */ 
        public function View(parent:DisplayObjectContainer)
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
        }

        /**
         * name_round.  Example:  TreeLeaves_0, TreeLeaves_1.
         */
        private function parseRounds():Array
        {
            var rounds:Array = [];
            var max:int = 0;
            var r:int;
            var parent:DisplayObjectContainer = screen.rounds;
            for (var c:int = 0; c < parent.numChildren; c++) {
                var child:MovieClip = parent.getChildAt(c) as MovieClip;
                if (child) {
                    var names:Array = child.name.split("_");
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
                        var names0:Array = getProperty(rounds[0], "name")
                        var namesR:Array = getProperty(rounds[r], "name")
                        throw new Error("Expected same number of items in each round.");
                    }
                    for (c = 0; c < rounds[r].length; c++) {
                        var name0:String = rounds[0][c].name.split("_")[0];
                        var name:String = rounds[r][c].name.split("_")[0];
                        if (name != name0) {
                            throw new Error("Expected name prefixes same.");
                        }
                        trace("View.parseRound: " + name + " round " + r);
                    }
                }
            }
            return rounds;
        }

        private function getProperty(items:Array, prop:String):Array
        {
            var props:Array = [];
            for (var i:int = 0; i < items.length; i++) {
                props.push(items[i][prop]);
            }
            return props;
        }

        /**
         * @return Index of MovieClip in screen.rounds.
         */
        internal function indexOf(stageX:int, stageY:int):int
        {
            var debugHit:Boolean = false;
            var point:Point = new Point(stageX, stageY);
            var hits:Array = screen.rounds.getObjectsUnderPoint(point);
            var found:DisplayObjectContainer;
            if (debugHit) {
                trace("View.indexOf: " + hits);
            }
            for (var h:int = hits.length - 1; 0 <= h; h--) {
                found = null;
                var hit:DisplayObject = hits[h];
                if (hit is MovieClip && screen.rounds != hit) {
                    found = hit as MovieClip;
                }
                else if (hit.parent && hit.parent is MovieClip && screen.rounds != hit.parent) {
                    found = hit.parent;
                }
                if (found) {
                    var bmp:BitmapData = new BitmapData(found.width, found.height, true, 0x00000000);
                    var matrix:Matrix = new Matrix();
                    var rect:Rectangle = found.getRect(found);
                    matrix.translate(-rect.x, -rect.y);
                    bmp.draw(found, matrix);
                    var p:Point = new Point(stageX, stageY);
                    p = found.globalToLocal(p);
                    p.x -= rect.left;
                    p.y -= rect.top;
                    var pixel:uint = bmp.getPixel32(p.x, p.y);
                    if (debugHit) { 
                        var bm:Bitmap = new Bitmap(bmp);
                        screen.addChild(bm);
                        if (found) {
                            trace("    name: " + found.name + " point " + p 
                                + " rect " + rect + " pixel " + pixel.toString(16));
                        }
                        var color:uint = 0x0000FF;
                        if (!pixel) {
                            found = null;
                            color = 0xFF0000;
                        }
                        var sprite:Sprite = new Sprite();
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
            var index:int = -1;
            for (var r:int = 0; r < rounds.length; r++) {
                index = rounds[r].indexOf(found);
                if (0 <= index) {
                    break;
                }
            }
            return index;
        }

        internal function end():void
        {
            backgroundClip.gotoAndPlay("end");
            screen.addFrameScript(screen.totalFrames - 1, screen.stop);
        }

        internal function hideScreen():void
        {
            // trace("View.hideScreen");
            if (reviewClip) {
                remove(reviewClip);
                reviewClip.visible = false;
            }
            screen.stop();
            screen.visible = false;
            remove(screen);
        }

        internal function populate(model:Model):void
        {
            this.model = model;
            for (var r:int = 0; r < rounds.length; r++) {
                for (var c:int = 0; c < rounds[r].length; c++) {
                    rounds[r][c].filters = [];
                }
            }
            if (!model.complete) {
                var previous:DisplayObject = rounds[model.round][model.target];
                previous.visible = false;
                var current:DisplayObject = rounds[model.round + 1][model.target];
                current.visible = true;
                if (model.trial < model.trialTutor) {
                    current.filters = [filterCorrect.clone()];
                    current.filters[0].strength = 6.0 - 0.05 * model.referee.percent;
                }
            }
        }

        internal function review():void
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
        }

        internal function win():void
        {
            if ("trial" != backgroundClip.currentLabel) {
                backgroundClip.gotoAndPlay("trial");
            }
        }

        internal function feedback(targetIndex:int,
                correct:Boolean):void
        {
            var target:DisplayObject = rounds[model.round][targetIndex];
            feedbackClip.x = target.x;
            feedbackClip.y = target.y;
            target.parent.addChild(feedbackClip);
            var label:String = correct ? "correct" : "wrong";
            feedbackClip.gotoAndPlay(label);
            target.filters = correct ? [filterCorrect.clone()]
                                        : [filterWrong.clone()];
        }

        internal function cancel():void
        {
        }

        internal function trialEnd():void
        {
            cancel();
            if ("end" != screen.currentLabel) {
                screen.gotoAndPlay("end");
            }
        }

        internal function clear():void
        {
            cancel();
        }

        internal function restart():void
        {
            hideScreen();
            clear();
            backgroundClip.stop();
            screen.stop();
            remove(backgroundClip);
        }

        internal static function remove(child:DisplayObject):void
        {
            if (null != child && null != child.parent && child.parent.contains(child)) {
                child.parent.removeChild(child);
            }
        }

        private static function removeAll(parent:DisplayObjectContainer):void
        {
            for (var c:int = parent.numChildren - 1; 0 <= c; c--) {
                remove(parent.getChildAt(c));
            }
        }
    }
}
