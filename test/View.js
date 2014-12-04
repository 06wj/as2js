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
        
    }


        /**
         * name_round.  Example:  TreeLeaves_0, TreeLeaves_1.
         */
            parseRounds: function()
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
    getProperty: function(items, prop)
    {

            var props:Array = [];
            for (var i:int = 0; i < items.length; i++) {
                props.push(items[i][prop]);
            
    }


        /**
         * @return Index of MovieClip in screen.rounds.
         */
            indexOf: function(stageX, stageY)
    {

            var debugHit:Boolean = false;
            var point:Point = new Point(stageX, stageY);
            var hits:Array = screen.rounds.getObjectsUnderPoint(point);
            var found:DisplayObjectContainer;
            if (debugHit) {
                trace("View.indexOf: " + hits);
            
    }
    end: function()
    {

            backgroundClip.gotoAndPlay("end");
            screen.addFrameScript(screen.totalFrames - 1, screen.stop);
        
    }
    hideScreen: function()
    {

            // trace("View.hideScreen");
            if (reviewClip) {
                remove(reviewClip);
                reviewClip.visible = false;
            
    }
    populate: function(model)
    {

            this.model = model;
            for (var r:int = 0; r < rounds.length; r++) {
                for (var c:int = 0; c < rounds[r].length; c++) {
                    rounds[r][c].filters = [];
                
    }
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
        
    }
    win: function()
    {

            if ("trial" != backgroundClip.currentLabel) {
                backgroundClip.gotoAndPlay("trial");
            
    }
    feedback: function(targetIndex, correct)
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
    cancel: function()
    {

        
    }
    trialEnd: function()
    {

            cancel();
            if ("end" != screen.currentLabel) {
                screen.gotoAndPlay("end");
            
    }
    clear: function()
    {

            cancel();
        
    }
    restart: function()
    {

            hideScreen();
            clear();
            backgroundClip.stop();
            screen.stop();
            remove(backgroundClip);
        
    }
});

