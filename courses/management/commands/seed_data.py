"""
python manage.py seed_data

Crée des utilisateurs, catégories, cours complets (modules + leçons),
quiz, inscriptions et messages de démonstration.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Remplit la base de données avec des données de démonstration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('⏳  Création des données de démo…'))
        self._create_users()
        self._create_categories()
        self._create_courses()
        self._create_quizzes()
        self._create_enrollments()
        self._create_live_sessions()
        self._create_classrooms()
        self.stdout.write(self.style.SUCCESS('\n✅  Base de données remplie avec succès !\n'))
        self.stdout.write('   Comptes disponibles :')
        self.stdout.write('   👩‍🏫  prof_marie   / pass1234  (professeur)')
        self.stdout.write('   👨‍🏫  prof_pierre  / pass1234  (professeur)')
        self.stdout.write('   👨‍🎓  etudiant_jean   / pass1234  (étudiant)')
        self.stdout.write('   👩‍🎓  etudiant_sarah  / pass1234  (étudiante)')
        self.stdout.write('   👨‍🎓  etudiant_paul   / pass1234  (étudiant)')
        self.stdout.write('   🔑  admin  / admin1234  (superadmin)\n')

    # ──────────────────────────────────────────────────────────────────────────
    def _create_users(self):
        from users.models import User
        self.stdout.write('  👤 Utilisateurs…')

        # Superadmin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin', email='admin@edujeunes.ht',
                password='admin1234', first_name='Admin', last_name='EduJeunes',
                role='admin'
            )

        # Professeurs
        teachers = [
            dict(username='prof_marie',  email='marie@edujeunes.ht',  first_name='Marie',  last_name='Joseph',  country='Haïti',
                 bio='Ingénieure logicielle avec 8 ans d\'expérience. Passionnée par l\'enseignement du code.', points=320),
            dict(username='prof_pierre', email='pierre@edujeunes.ht', first_name='Pierre', last_name='Dupont', country='Haïti',
                 bio='Mathématicien et physicien. Professeur depuis 10 ans au lycée Henri Christophe.', points=280),
            dict(username='prof_anne',   email='anne@edujeunes.ht',   first_name='Anne',   last_name='Claire',  country='Haïti',
                 bio='Designer UX/UI et artiste digitale. J\'enseigne le design créatif aux jeunes.', points=190),
        ]
        for t in teachers:
            if not User.objects.filter(username=t['username']).exists():
                u = User.objects.create_user(password='pass1234', role='teacher', **t)
                self.stdout.write(f'    ✓ {u.display_name}')

        # Étudiants
        students = [
            dict(username='etudiant_jean',  email='jean@mail.ht',  first_name='Jean',  last_name='Baptiste', country='Haïti',   points=150),
            dict(username='etudiant_sarah', email='sarah@mail.ht', first_name='Sarah', last_name='Moreau',   country='Haïti',   points=210),
            dict(username='etudiant_paul',  email='paul@mail.ht',  first_name='Paul',  last_name='Alexis',   country='Haïti',   points=90),
            dict(username='etudiant_rose',  email='rose@mail.ht',  first_name='Rose',  last_name='Pierre',   country='Haïti',   points=175),
            dict(username='etudiant_marc',  email='marc@mail.ht',  first_name='Marc',  last_name='Henry',    country='Canada',  points=60),
        ]
        for s in students:
            if not User.objects.filter(username=s['username']).exists():
                u = User.objects.create_user(password='pass1234', role='student', **s)
                self.stdout.write(f'    ✓ {u.display_name}')

    # ──────────────────────────────────────────────────────────────────────────
    def _create_categories(self):
        from courses.models import Category
        self.stdout.write('  📂 Catégories…')
        cats = [
            ('Programmation',  'bi-code-slash',    '#58a6ff'),
            ('Mathématiques',  'bi-calculator',    '#3fb950'),
            ('Sciences',       'bi-flask',         '#d29922'),
            ('Langues',        'bi-translate',     '#a371f7'),
            ('Design',         'bi-palette',       '#FF6B2B'),
            ('Histoire',       'bi-book-half',     '#f85149'),
            ('Musique',        'bi-music-note',    '#e879f9'),
            ('Entrepreneuriat','bi-graph-up-arrow','#38bdf8'),
        ]
        for name, icon, color in cats:
            c, created = Category.objects.get_or_create(name=name, defaults={'icon': icon, 'color': color})
            if created:
                self.stdout.write(f'    ✓ {name}')

    # ──────────────────────────────────────────────────────────────────────────
    def _create_courses(self):
        from users.models import User
        from courses.models import Category, Course, Module, Lesson
        self.stdout.write('  📚 Cours…')

        marie  = User.objects.get(username='prof_marie')
        pierre = User.objects.get(username='prof_pierre')
        anne   = User.objects.get(username='prof_anne')

        cat_prog   = Category.objects.get(name='Programmation')
        cat_maths  = Category.objects.get(name='Mathématiques')
        cat_design = Category.objects.get(name='Design')
        cat_sc     = Category.objects.get(name='Sciences')
        cat_lang   = Category.objects.get(name='Langues')

        courses_data = [
            # ── COURS 1 ──
            dict(
                title='Python pour Débutants', teacher=marie, category=cat_prog,
                level='beginner', status='published', is_free=True, language='Français',
                description='Apprends Python de zéro ! Ce cours complet t\'enseigne les bases de la programmation avec Python, le langage le plus populaire du monde.',
                what_you_learn='Variables et types de données · Conditions et boucles · Fonctions et modules · Fichiers et exceptions · Mini-projets pratiques',
                requirements='Aucun prérequis. Juste un ordinateur et la motivation !',
                modules=[
                    dict(title='Introduction à Python', description='Premiers pas avec Python', lessons=[
                        dict(title='Qu\'est-ce que Python ?',          type='video', url='https://www.youtube.com/embed/kqtD5dpn9C8', dur=12, preview=True),
                        dict(title='Installer Python & VS Code',       type='video', url='https://www.youtube.com/embed/9o4gDQvVkLU', dur=10, preview=True),
                        dict(title='Ton premier programme : Hello World', type='text',
                             content='Dans cette leçon nous allons écrire notre tout premier programme Python.\n\n```python\nprint("Bonjour le monde !")\n```\n\nLe mot-clé `print()` permet d\'afficher du texte. C\'est la base de tout programme Python.', dur=8),
                    ]),
                    dict(title='Variables et Types', description='Les fondamentaux', lessons=[
                        dict(title='Les variables',         type='video', url='https://www.youtube.com/embed/cltFQLrZX-o', dur=15),
                        dict(title='Nombres et calculs',    type='video', url='https://www.youtube.com/embed/khKv-8q7YmY', dur=18),
                        dict(title='Les chaînes de texte',  type='video', url='https://www.youtube.com/embed/k9TUPpGqYTo', dur=14),
                        dict(title='Exercices pratiques',   type='text',
                             content='**Exercice 1 :** Créez une variable `nom` avec votre prénom et affichez-la.\n**Exercice 2 :** Calculez la surface d\'un rectangle 5×8.\n**Exercice 3 :** Concaténez deux chaînes de texte.', dur=20),
                    ]),
                    dict(title='Conditions et Boucles', description='La logique de programmation', lessons=[
                        dict(title='Les conditions if/else', type='video', url='https://www.youtube.com/embed/f4KOjWS_KZs', dur=16),
                        dict(title='La boucle for',          type='video', url='https://www.youtube.com/embed/jn3x1i28GVU', dur=14),
                        dict(title='La boucle while',        type='video', url='https://www.youtube.com/embed/HZARImviDxg', dur=12),
                        dict(title='Quiz : Boucles',         type='live',  url='', dur=0),
                    ]),
                    dict(title='Fonctions', description='Organiser son code', lessons=[
                        dict(title='Définir une fonction',     type='video', url='https://www.youtube.com/embed/NSbOtYzIQI0', dur=20),
                        dict(title='Paramètres et retour',     type='video', url='https://www.youtube.com/embed/89cGQjB5R4M', dur=18),
                        dict(title='Fonctions lambda',         type='text',
                             content='Les fonctions lambda sont des fonctions anonymes sur une seule ligne.\n\n```python\ndouble = lambda x: x * 2\nprint(double(5))  # → 10\n```\n\nElles sont utiles pour les opérations simples.', dur=10),
                    ]),
                ]
            ),
            # ── COURS 2 ──
            dict(
                title='Algèbre Linéaire — Du Lycée à l\'Université',
                teacher=pierre, category=cat_maths,
                level='intermediate', status='published', is_free=True, language='Français',
                description='Maîtrise l\'algèbre linéaire : vecteurs, matrices, systèmes d\'équations et espaces vectoriels expliqués simplement.',
                what_you_learn='Vecteurs et opérations · Matrices et déterminants · Systèmes linéaires · Valeurs propres · Applications concrètes',
                requirements='Niveau terminale en mathématiques.',
                modules=[
                    dict(title='Les Vecteurs', description='Introduction aux vecteurs', lessons=[
                        dict(title='Qu\'est-ce qu\'un vecteur ?', type='video', url='https://www.youtube.com/embed/fNk_zzaMoSs', dur=14, preview=True),
                        dict(title='Addition de vecteurs',        type='video', url='https://www.youtube.com/embed/ml4NSzCQobk', dur=16),
                        dict(title='Produit scalaire',            type='text',
                             content='Le produit scalaire de deux vecteurs **a** et **b** est défini par :\n\na · b = |a| × |b| × cos(θ)\n\nOù θ est l\'angle entre les deux vecteurs.\n\n**Application :** Si a = (3, 4) et b = (1, 2), alors :\na · b = 3×1 + 4×2 = 11', dur=18),
                    ]),
                    dict(title='Les Matrices', description='Calcul matriciel', lessons=[
                        dict(title='Introduction aux matrices',        type='video', url='https://www.youtube.com/embed/0oGJTQCy4cQ', dur=20),
                        dict(title='Multiplication de matrices',       type='video', url='https://www.youtube.com/embed/XkY2DOUCWMU', dur=22),
                        dict(title='Déterminant et inverse',           type='video', url='https://www.youtube.com/embed/uQhTuRlWMxw', dur=25),
                        dict(title='Exercices corrigés — Matrices',    type='audio', url='', dur=30),
                    ]),
                    dict(title='Systèmes d\'Équations', description='Résolution de systèmes', lessons=[
                        dict(title='Méthode de Gauss',           type='video', url='https://www.youtube.com/embed/2tlwSqblrvU', dur=28),
                        dict(title='Méthode de Cramer',          type='video', url='https://www.youtube.com/embed/jBsC34PxzoM', dur=20),
                        dict(title='Applications économiques',   type='text',
                             content='Les systèmes d\'équations linéaires sont utilisés partout :\n\n• En économie pour modéliser l\'offre et la demande\n• En physique pour les circuits électriques\n• En informatique pour le rendu 3D\n\nExemple concret : Trouver les prix d\'équilibre de deux marchés interdépendants.', dur=15),
                    ]),
                ]
            ),
            # ── COURS 3 ──
            dict(
                title='Design Web Moderne avec Figma & CSS',
                teacher=anne, category=cat_design,
                level='beginner', status='published', is_free=True, language='Français',
                description='Apprends à créer des interfaces web magnifiques. De Figma pour les maquettes jusqu\'au CSS avancé pour l\'implémentation.',
                what_you_learn='Principes du design · Figma de A à Z · HTML/CSS modernes · Animations CSS · Responsive design',
                requirements='Notions de base en informatique suffisent.',
                modules=[
                    dict(title='Principes du Design', description='Les bases du bon design', lessons=[
                        dict(title='Les 4 principes du design', type='video', url='https://www.youtube.com/embed/a5KYlHNKQB8', dur=18, preview=True),
                        dict(title='Théorie des couleurs',      type='video', url='https://www.youtube.com/embed/AvgCkHrcj8w', dur=22, preview=True),
                        dict(title='Typographie pour le web',   type='text',
                             content='La typographie est l\'art d\'organiser le texte.\n\n**Règles essentielles :**\n• Maximum 2-3 polices par page\n• Contraste minimum de 4.5:1 pour l\'accessibilité\n• Taille minimale : 16px pour le corps du texte\n• Line-height : 1.5 à 1.8 pour la lisibilité\n\nOutils recommandés : Google Fonts, Fontpair.co', dur=15),
                    ]),
                    dict(title='Figma de A à Z', description='Maîtriser Figma', lessons=[
                        dict(title='Interface et outils de base',    type='video', url='https://www.youtube.com/embed/FTFaQWZBqQ8', dur=25),
                        dict(title='Composants et auto-layout',      type='video', url='https://www.youtube.com/embed/TyaGpGDFczw', dur=30),
                        dict(title='Prototypage interactif',         type='video', url='https://www.youtube.com/embed/F5x5KJMwLgY', dur=20),
                        dict(title='Exporter et partager',           type='video', url='https://www.youtube.com/embed/PaPL3R_MHLA', dur=12),
                    ]),
                    dict(title='CSS Avancé', description='Animations et mise en page', lessons=[
                        dict(title='Flexbox de zéro',            type='video', url='https://www.youtube.com/embed/fYq5PXgSsbE', dur=28),
                        dict(title='CSS Grid',                   type='video', url='https://www.youtube.com/embed/9zBsdzdE4sM', dur=25),
                        dict(title='Animations CSS',             type='video', url='https://www.youtube.com/embed/YszONjKpgg4', dur=22),
                        dict(title='Mini-projet : Portfolio',    type='text',
                             content='**Projet final :** Crée ton portfolio personnel.\n\nÉtapes :\n1. Maquetter dans Figma (header, about, projets, contact)\n2. Intégrer en HTML/CSS\n3. Ajouter des animations d\'entrée\n4. Rendre responsive (mobile first)\n\nRessources : CodePen.io pour tester, Netlify pour héberger gratuitement.', dur=60),
                    ]),
                ]
            ),
            # ── COURS 4 ──
            dict(
                title='Physique Quantique — Introduction',
                teacher=pierre, category=cat_sc,
                level='advanced', status='published', is_free=True, language='Français',
                description='Une introduction accessible à la physique quantique. Comprends les phénomènes qui régissent le monde à l\'échelle atomique.',
                what_you_learn='Dualité onde-corpuscule · Principe d\'incertitude · Équation de Schrödinger · Intrication quantique',
                requirements='Physique terminale + bases de mathématiques (dérivées, intégrales).',
                modules=[
                    dict(title='Les Bases du Quantique', description='Comprendre le monde subatomique', lessons=[
                        dict(title='L\'atome de Bohr',             type='video', url='https://www.youtube.com/embed/GuFui3y_JgE', dur=20, preview=True),
                        dict(title='La dualité onde-corpuscule',   type='video', url='https://www.youtube.com/embed/Iim4GbJLfGU', dur=25),
                        dict(title='L\'expérience des doubles fentes', type='video', url='https://www.youtube.com/embed/H6HLjpj4Nt4', dur=18),
                    ]),
                    dict(title='Principe d\'incertitude', description='Heisenberg et ses implications', lessons=[
                        dict(title='Heisenberg — Principe d\'incertitude', type='video', url='https://www.youtube.com/embed/TQKELOE9eY4', dur=22),
                        dict(title='Conséquences philosophiques',          type='text',
                             content='Le principe d\'incertitude d\'Heisenberg stipule qu\'on ne peut pas connaître simultanément la position et la vitesse d\'une particule avec une précision infinie.\n\nΔx · Δp ≥ ℏ/2\n\nCeci n\'est pas une limitation de nos instruments mais une propriété fondamentale de la nature.', dur=15),
                    ]),
                ]
            ),
            # ── COURS 5 ──
            dict(
                title='Anglais Business pour Professionnels',
                teacher=anne, category=cat_lang,
                level='intermediate', status='published', is_free=False, price=25, language='Anglais',
                description='Maîtrise l\'anglais professionnel pour booster ta carrière. Emails, présentations, négociations et networking en anglais.',
                what_you_learn='Emails professionnels · Présentations orales · Vocabulaire business · Négociation · Entretiens d\'embauche',
                requirements='Niveau A2-B1 en anglais.',
                modules=[
                    dict(title='Business Writing', description='Écrire professionnellement', lessons=[
                        dict(title='Professional Email Basics',        type='video', url='https://www.youtube.com/embed/gChVIxH7X0E', dur=20, preview=True),
                        dict(title='Writing Subject Lines that Work',  type='video', url='https://www.youtube.com/embed/LDqo3Hs27uc', dur=15),
                        dict(title='Common Business Phrases',          type='text',
                             content='**Essential business phrases :**\n\n• "I am writing to inform you that…"\n• "Please find attached…"\n• "I look forward to hearing from you"\n• "As per our conversation…"\n• "Could you please clarify…"\n• "I would appreciate your prompt response"\n\nPractice: Write an email requesting a meeting.', dur=20),
                    ]),
                    dict(title='Presentations & Meetings', description='Speak with confidence', lessons=[
                        dict(title='Structuring a Presentation',       type='video', url='https://www.youtube.com/embed/Unzc731iCUY', dur=25),
                        dict(title='Meeting Vocabulary & Phrases',     type='audio', url='', dur=35),
                        dict(title='Negotiation Techniques',           type='video', url='https://www.youtube.com/embed/MqEpQMInMp8', dur=28),
                    ]),
                ]
            ),
            # ── COURS 6 ──
            dict(
                title='Développement Web Full-Stack avec Django',
                teacher=marie, category=cat_prog,
                level='intermediate', status='published', is_free=False, price=15, language='Français',
                description='Deviens développeur full-stack avec Django. Crée des applications web complètes de la base de données à l\'interface utilisateur.',
                what_you_learn='Django MVT · Modèles & migrations · Templates & vues · API REST · Déploiement',
                requirements='Bases de Python (idéalement notre cours Python Débutants).',
                modules=[
                    dict(title='Introduction à Django', description='Le framework web Python', lessons=[
                        dict(title='Pourquoi Django ?',                type='video', url='https://www.youtube.com/embed/rHux0gMZ3Eg', dur=12, preview=True),
                        dict(title='Installation et premier projet',   type='video', url='https://www.youtube.com/embed/UmljXZIypDc', dur=20),
                        dict(title='Architecture MVT',                 type='text',
                             content='Django suit le pattern **MVT** (Model-View-Template) :\n\n• **Model** : Définit la structure des données (base de données)\n• **View** : Contient la logique métier\n• **Template** : Gère l\'affichage HTML\n\nC\'est similaire au MVC mais avec les templates à la place des vues traditionnelles.', dur=15),
                    ]),
                    dict(title='Modèles et Base de Données', description='ORM Django', lessons=[
                        dict(title='Créer ses modèles',         type='video', url='https://www.youtube.com/embed/EHuKZE-QxsA', dur=25),
                        dict(title='Migrations',                type='video', url='https://www.youtube.com/embed/cR3j_FXJMZA', dur=18),
                        dict(title='Django Admin',              type='video', url='https://www.youtube.com/embed/jMkFzAKy9vI', dur=20),
                        dict(title='ORM et QuerySets',          type='video', url='https://www.youtube.com/embed/FHZn-I_4qXQ', dur=30),
                    ]),
                    dict(title='Vues et Templates', description='L\'interface utilisateur', lessons=[
                        dict(title='Function-Based Views',      type='video', url='https://www.youtube.com/embed/mbA83JU5ZIk', dur=22),
                        dict(title='Templates Django',          type='video', url='https://www.youtube.com/embed/4hZ0f-6Uf2s', dur=25),
                        dict(title='Formulaires',               type='video', url='https://www.youtube.com/embed/6oOHlcHkX2U', dur=28),
                        dict(title='Authentification',          type='video', url='https://www.youtube.com/embed/H4oxNSJmIzs', dur=20),
                    ]),
                ]
            ),
        ]

        for cd in courses_data:
            modules_data = cd.pop('modules')
            if Course.objects.filter(title=cd['title']).exists():
                self.stdout.write(f'    (existe déjà) {cd["title"]}')
                continue
            course = Course.objects.create(**cd)
            self.stdout.write(f'    ✓ {course.title}')
            for i, md in enumerate(modules_data):
                lessons_data = md.pop('lessons')
                mod = Module.objects.create(course=course, order=i, **md)
                for j, ld in enumerate(lessons_data):
                    Lesson.objects.create(
                        module=mod, order=j,
                        title=ld['title'],
                        lesson_type=ld['type'],
                        video_url=ld.get('url', ''),
                        content=ld.get('content', ''),
                        duration_minutes=ld.get('dur', 0),
                        is_preview=ld.get('preview', False),
                    )

    # ──────────────────────────────────────────────────────────────────────────
    def _create_quizzes(self):
        from courses.models import Course
        from quiz.models import Quiz, Question, Choice
        self.stdout.write('  📝 Quiz…')

        course = Course.objects.filter(title__icontains='Python pour').first()
        if not course or Quiz.objects.filter(course=course).exists():
            return

        quiz = Quiz.objects.create(
            course=course,
            title='Quiz — Les bases de Python',
            description='Teste tes connaissances sur les fondamentaux de Python.',
            time_limit_minutes=15,
            passing_score=60,
            max_attempts=3,
        )

        questions = [
            dict(
                text='Quel mot-clé est utilisé pour afficher du texte en Python ?',
                type='single', pts=1,
                choices=[('print()', True), ('echo()', False), ('display()', False), ('show()', False)]
            ),
            dict(
                text='Quelle est la syntaxe correcte pour créer une variable en Python ?',
                type='single', pts=1,
                choices=[('x = 5', True), ('int x = 5', False), ('var x = 5', False), ('x := 5', False)]
            ),
            dict(
                text='Quels types de données existent en Python ? (plusieurs réponses)',
                type='multiple', pts=2,
                choices=[('int', True), ('str', True), ('float', True), ('char', False)]
            ),
            dict(
                text='Comment écrire un commentaire sur une seule ligne en Python ?',
                type='single', pts=1,
                choices=[('# Commentaire', True), ('// Commentaire', False), ('/* Commentaire */', False), ('<!-- Commentaire -->', False)]
            ),
            dict(
                text='Quelle boucle est utilisée quand on connaît le nombre d\'itérations ?',
                type='single', pts=1,
                choices=[('for', True), ('while', False), ('loop', False), ('repeat', False)]
            ),
            dict(
                text='Qu\'affiche print(2 ** 3) ?',
                type='single', pts=1,
                choices=[('8', True), ('6', False), ('5', False), ('9', False)],
                explanation='L\'opérateur ** est la puissance en Python. 2³ = 8.'
            ),
        ]

        for i, qd in enumerate(questions):
            q = Question.objects.create(
                quiz=quiz, text=qd['text'],
                question_type=qd['type'], points=qd['pts'],
                order=i, explanation=qd.get('explanation', '')
            )
            for j, (text, correct) in enumerate(qd['choices']):
                Choice.objects.create(question=q, text=text, is_correct=correct, order=j)

        self.stdout.write(f'    ✓ Quiz créé pour {course.title}')

        # Quiz 2 — Design
        course2 = Course.objects.filter(title__icontains='Design Web').first()
        if course2 and not Quiz.objects.filter(course=course2).exists():
            quiz2 = Quiz.objects.create(
                course=course2, title='Quiz — Principes du design',
                description='Vérifie ta compréhension des bases du design web.',
                time_limit_minutes=10, passing_score=70, max_attempts=3,
            )
            q1 = Question.objects.create(quiz=quiz2, text='Quels sont les 4 principes du design CRAP ?', question_type='multiple', points=2, order=0)
            for j, (t, c) in enumerate([('Contraste', True), ('Répétition', True), ('Alignement', True), ('Proximité', True), ('Couleur', False)]):
                Choice.objects.create(question=q1, text=t, is_correct=c, order=j)
            q2 = Question.objects.create(quiz=quiz2, text='Quelle propriété CSS crée un conteneur flexible ?', question_type='single', points=1, order=1)
            for j, (t, c) in enumerate([('display: flex', True), ('display: block', False), ('display: grid', False), ('position: flex', False)]):
                Choice.objects.create(question=q2, text=t, is_correct=c, order=j)
            self.stdout.write(f'    ✓ Quiz créé pour {course2.title}')

    # ──────────────────────────────────────────────────────────────────────────
    def _create_enrollments(self):
        from users.models import User
        from courses.models import Course, Enrollment, LessonProgress
        from quiz.models import Quiz, QuizAttempt, Answer
        self.stdout.write('  🎓 Inscriptions…')

        jean  = User.objects.get(username='etudiant_jean')
        sarah = User.objects.get(username='etudiant_sarah')
        paul  = User.objects.get(username='etudiant_paul')
        rose  = User.objects.get(username='etudiant_rose')
        marc  = User.objects.get(username='etudiant_marc')

        courses = list(Course.objects.filter(status='published'))

        enrollments = [
            (jean,  'Python pour Débutants', 65),
            (jean,  'Développement Web Full-Stack', 20),
            (jean,  'Algèbre Linéaire', 10),
            (sarah, 'Python pour Débutants', 100),
            (sarah, 'Design Web Moderne', 45),
            (sarah, 'Anglais Business', 30),
            (paul,  'Algèbre Linéaire', 55),
            (paul,  'Physique Quantique', 15),
            (rose,  'Design Web Moderne', 80),
            (rose,  'Anglais Business', 60),
            (rose,  'Python pour Débutants', 35),
            (marc,  'Python pour Débutants', 5),
            (marc,  'Développement Web Full-Stack', 0),
        ]

        for student, course_title, progress in enrollments:
            course = Course.objects.filter(title__icontains=course_title.split()[0]).first()
            if not course:
                continue
            enr, created = Enrollment.objects.get_or_create(
                student=student, course=course,
                defaults={'progress': progress, 'completed': progress >= 100}
            )
            if created and progress > 0:
                from courses.models import Lesson as LessonModel
                all_lessons = list(
                    LessonModel.objects
                    .filter(module__course=course)
                    .order_by('module__order', 'order')
                )
                n_done = int(len(all_lessons) * progress / 100)
                for les in all_lessons[:n_done]:
                    LessonProgress.objects.get_or_create(
                        student=student, lesson=les,
                        defaults={'completed': True, 'completed_at': timezone.now()}
                    )
        self.stdout.write(f'    ✓ {len(enrollments)} inscriptions créées')

        # Add some reviews
        from courses.models import Review
        reviews_data = [
            (sarah, 'Python pour Débutants', 5, 'Excellent cours ! Très bien expliqué, j\'ai tout compris. Je recommande à tous les débutants.'),
            (jean,  'Python pour Débutants', 4, 'Super contenu. Les vidéos sont claires. Juste quelques exercices supplémentaires seraient bien.'),
            (rose,  'Design Web Moderne',    5, 'Marie est une excellente professeure ! Les projets pratiques sont très utiles.'),
            (sarah, 'Design Web Moderne',    4, 'Très bon cours. J\'ai appris Figma en une semaine grâce à ce cours.'),
            (paul,  'Algèbre Linéaire',      5, 'Pierre explique très clairement. Enfin je comprends les matrices !'),
        ]
        for student, course_title, rating, comment in reviews_data:
            course = Course.objects.filter(title__icontains=course_title.split()[0]).first()
            if course:
                Review.objects.get_or_create(
                    course=course, student=student,
                    defaults={'rating': rating, 'comment': comment}
                )
        self.stdout.write('    ✓ Avis ajoutés')

    # ──────────────────────────────────────────────────────────────────────────
    def _create_live_sessions(self):
        from users.models import User
        from courses.models import Course
        from live.models import LiveSession
        import secrets
        self.stdout.write('  📡 Sessions live…')

        marie  = User.objects.get(username='prof_marie')
        pierre = User.objects.get(username='prof_pierre')

        course_py  = Course.objects.filter(title__icontains='Python pour').first()
        course_math = Course.objects.filter(title__icontains='Algèbre').first()
        course_dj  = Course.objects.filter(title__icontains='Django').first()

        sessions = [
            dict(course=course_py,   teacher=marie,  title='Session Q&A — Module Python : Fonctions',    status='scheduled', scheduled_at=timezone.now() + timedelta(days=2, hours=3)),
            dict(course=course_math, teacher=pierre, title='Correction exercices — Matrices',             status='scheduled', scheduled_at=timezone.now() + timedelta(days=5, hours=2)),
            dict(course=course_dj,   teacher=marie,  title='Live Coding — Construire une API REST',       status='live',      scheduled_at=timezone.now() - timedelta(hours=1)),
            dict(course=course_py,   teacher=marie,  title='Introduction Python — Récap Complet',         status='ended',     scheduled_at=timezone.now() - timedelta(days=7)),
            dict(course=course_math, teacher=pierre, title='Valeurs propres et vecteurs propres',         status='scheduled', scheduled_at=timezone.now() + timedelta(days=10)),
        ]

        for sd in sessions:
            if sd['course'] and not LiveSession.objects.filter(title=sd['title']).exists():
                LiveSession.objects.create(
                    description=f"Session live interactive pour le cours {sd['course'].title}.",
                    is_recorded=True,
                    stream_key=secrets.token_hex(16),
                    **sd
                )
        self.stdout.write('    ✓ Sessions live créées')

    # ──────────────────────────────────────────────────────────────────────────
    def _create_classrooms(self):
        from courses.models import Course
        from chat.models import Classroom, Message
        from users.models import User
        self.stdout.write('  💬 Classrooms…')

        courses = Course.objects.filter(status='published')
        jean  = User.objects.filter(username='etudiant_jean').first()
        sarah = User.objects.filter(username='etudiant_sarah').first()
        marie = User.objects.filter(username='prof_marie').first()

        for course in courses:
            room, created = Classroom.objects.get_or_create(course=course)
            if created and course.title.__contains__('Python') and jean and sarah and marie:
                msgs = [
                    (marie, 'Bienvenue dans le classroom de ce cours ! N\'hésitez pas à poser vos questions ici. 😊'),
                    (jean,  'Bonjour ! J\'ai une question sur les fonctions lambda. Comment les utiliser avec map() ?'),
                    (sarah, 'Bonjour Jean ! Tu peux écrire : list(map(lambda x: x*2, [1,2,3])). Ça donne [2,4,6].'),
                    (jean,  'Merci Sarah ! Très clair. Et pour filter() ?'),
                    (marie, 'Excellente question Jean ! filter(lambda x: x > 2, [1,2,3,4]) → [3,4]. Je ferai un live là-dessus la semaine prochaine 📹'),
                    (sarah, 'Super ! J\'ai hâte. Est-ce qu\'on abordera aussi les comprehensions ?'),
                    (marie, 'Absolument ! Les list comprehensions sont encore plus puissantes. [x*2 for x in range(5) if x > 0]'),
                ]
                for sender, content in msgs:
                    Message.objects.create(classroom=room, sender=sender, content=content)
        self.stdout.write('    ✓ Classrooms et messages créés')
