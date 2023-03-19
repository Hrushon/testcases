from django.contrib import admin

from .models import (Answer, Question, Test, Theme,
                     UserQuestionAnswer, UserTest)


class AnswerAdmin(admin.ModelAdmin):
    search_fields = ('body_text',)
    list_display = ('body_text',)


class AnswerInline(admin.TabularInline):
    model = Answer


class ThemeAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title',)


class UserTestInline(admin.TabularInline):
    model = UserTest


class QuestionInline(admin.TabularInline):
    model = Question


class TestAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_filter = ('title', 'theme', 'date_creation', 'author', 'prize',)
    list_display = ('title', 'theme',)
    list_editable = ('theme',)
    readonly_fields = ('questions_count',)
    inlines = (UserTestInline, QuestionInline,)

    def questions_count(self, instance):
        return instance.questions.count()

    questions_count.short_description = 'Количество вопросов'


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('body_text',)
    list_display = ('body_text', 'test_base',)
    list_filter = ('test_base', 'one_correct_answer',)
    list_editable = ('test_base',)
    inlines = (AnswerInline,)


class UserQuestionAnswerAdmin(admin.ModelAdmin):
    list_filter = ('date_answering',)


admin.site.register(Answer, AnswerAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(UserQuestionAnswer, UserQuestionAnswerAdmin)
