from django.contrib import admin

from .models import Answer, Attempt, Question, Test, TestingData, Theme


class AnswerAdmin(admin.ModelAdmin):
    search_fields = ('answer_text',)
    list_display = ('answer_text',)


class AnswerInline(admin.TabularInline):
    model = Answer


class ThemeAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title',)


class UsersAttemptInline(admin.TabularInline):
    model = Attempt


class QuestionInline(admin.TabularInline):
    model = Question


class TestAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_filter = ('title', 'theme', 'date_creation', 'author', 'prize',)
    list_display = ('title', 'theme',)
    list_editable = ('theme',)
    readonly_fields = ('questions_count',)
    inlines = (UsersAttemptInline, QuestionInline,)

    def questions_count(self, instance):
        return instance.questions.count()

    questions_count.short_description = 'Количество вопросов'


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('question_text',)
    list_display = ('question_text', 'test_base',)
    list_filter = ('test_base',)
    list_editable = ('test_base',)
    inlines = (AnswerInline,)


class TestingDataAdmin(admin.ModelAdmin):
    list_filter = ('attempt',)


admin.site.register(Answer, AnswerAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(TestingData, TestingDataAdmin)
