from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Quiz, Question, Choice, QuizAttempt, Answer


@login_required
def quiz_detail(request, quiz_id):
    quiz     = get_object_or_404(Quiz, id=quiz_id)
    attempts = QuizAttempt.objects.filter(student=request.user, quiz=quiz)
    can_try  = attempts.count() < quiz.max_attempts
    return render(request, 'quiz/detail.html', {
        'quiz': quiz, 'attempts': attempts, 'can_try': can_try
    })


@login_required
def take_quiz(request, quiz_id):
    quiz       = get_object_or_404(Quiz, id=quiz_id)
    prev_count = QuizAttempt.objects.filter(student=request.user, quiz=quiz).count()
    if prev_count >= quiz.max_attempts:
        messages.error(request, "Nombre maximum de tentatives atteint.")
        return redirect('quiz_detail', quiz_id=quiz_id)

    if request.method == 'POST':
        attempt = QuizAttempt.objects.create(
            student=request.user, quiz=quiz, attempt_number=prev_count + 1
        )
        total_pts = 0
        earned    = 0
        for q in quiz.questions.all():
            total_pts += q.points
            ans = Answer.objects.create(attempt=attempt, question=q)
            if q.question_type in ('single', 'multiple'):
                ids = request.POST.getlist(f'q_{q.id}')
                sel = Choice.objects.filter(id__in=ids)
                ans.selected_choices.set(sel)
                correct_ids = set(q.choices.filter(is_correct=True).values_list('id', flat=True))
                if correct_ids == set(int(i) for i in ids):
                    ans.is_correct = True
                    earned += q.points
            else:
                ans.text_answer = request.POST.get(f'q_{q.id}', '').strip()
            ans.save()

        score           = (earned / total_pts * 100) if total_pts else 0
        attempt.score   = round(score, 1)
        attempt.passed  = score >= quiz.passing_score
        attempt.finished_at = timezone.now()
        attempt.save()
        if attempt.passed:
            request.user.points += 10
            request.user.save()
        return redirect('quiz_result', attempt_id=attempt.id)

    questions = quiz.questions.prefetch_related('choices').all()
    return render(request, 'quiz/take.html', {'quiz': quiz, 'questions': questions})


@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    answers = attempt.answers.select_related('question').prefetch_related(
        'selected_choices', 'question__choices'
    )
    return render(request, 'quiz/result.html', {'attempt': attempt, 'answers': answers})
