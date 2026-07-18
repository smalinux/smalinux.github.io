/* quiz.js — the retrieval-practice widget shared by every lesson.
   Reuse it; don't inline a second copy.

   Markup contract:

     <div class="quiz" data-quiz>
       <div class="quiz-q" data-answer="pol">
         <p class="quiz-prompt">Some rule to place.</p>
         <div class="quiz-choices">
           <button data-choice="pol">politeness.py</button>
           <button data-choice="lim">limits.py</button>
         </div>
         <div class="quiz-fb"><p>Why that is the answer.</p></div>
       </div>
       ...
       <p class="quiz-score" data-quiz-score></p>
     </div>

   Feedback is immediate and automatic — the tightest loop we can give without
   a human in it. A question locks after the first click: the point is to make
   you retrieve, not to let you hunt for the green one.

   The widget is lesson-agnostic. The choices can be any two labels (module
   names, "closes it" / "stays open", …) — only data-choice / data-answer
   matter. A lesson may override the end-of-quiz flourish with data-perfect and
   data-partial attributes on the [data-quiz] container; both default to generic
   copy so a lesson that sets neither still reads well. */

(function () {
  "use strict";

  function initQuiz(quiz) {
    var questions = Array.prototype.slice.call(quiz.querySelectorAll(".quiz-q"));
    var scoreEl = quiz.querySelector("[data-quiz-score]");
    var answered = 0;
    var correct = 0;

    var perfectMsg =
      quiz.getAttribute("data-perfect") ||
      "— all correct. Come back tomorrow and retrieve it cold; that is when it sticks.";
    var partialMsg =
      quiz.getAttribute("data-partial") ||
      "— revisit the ones you missed, then retry the set from memory.";

    function renderScore() {
      if (!scoreEl) return;
      if (answered === 0) {
        scoreEl.textContent = "";
        return;
      }
      var msg = correct + " / " + questions.length + " correct";
      if (answered === questions.length) {
        msg += " " + (correct === questions.length ? perfectMsg : partialMsg);
      }
      scoreEl.textContent = msg;
    }

    questions.forEach(function (q) {
      var expected = q.getAttribute("data-answer");
      var buttons = Array.prototype.slice.call(q.querySelectorAll("[data-choice]"));
      var feedback = q.querySelector(".quiz-fb");

      buttons.forEach(function (btn) {
        btn.addEventListener("click", function () {
          if (q.classList.contains("answered")) return;
          q.classList.add("answered");
          answered += 1;

          var chosen = btn.getAttribute("data-choice");
          var isRight = chosen === expected;
          if (isRight) correct += 1;

          btn.classList.add(isRight ? "chosen-right" : "chosen-wrong");
          if (!isRight) {
            buttons.forEach(function (other) {
              if (other.getAttribute("data-choice") === expected) {
                other.classList.add("was-right");
              }
            });
          }
          buttons.forEach(function (b) { b.disabled = true; });
          if (feedback) feedback.classList.add("shown");
          renderScore();
        });
      });
    });

    renderScore();
  }

  function boot() {
    Array.prototype.slice.call(document.querySelectorAll("[data-quiz]")).forEach(initQuiz);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
