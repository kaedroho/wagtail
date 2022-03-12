from django import forms
from django.test import TestCase, override_settings

from wagtail.admin import widgets
from wagtail.admin.widgets import AdminDateTimeInput
from wagtail.videos import models
from wagtail.videos.forms import BaseVideoForm, get_video_base_form, get_video_form
from wagtail.tests.testapp.media_forms import AlternateVideoForm, OverriddenWidget


class TestVideoFormOverride(TestCase):
    def test_get_video_base_form(self):
        self.assertIs(get_video_base_form(), BaseVideoForm)

    def test_get_video_form(self):
        bases = get_video_form(models.Video).__bases__
        self.assertIn(BaseVideoForm, bases)
        self.assertNotIn(AlternateVideoForm, bases)

    def test_get_video_form_widgets(self):
        form_cls = get_video_form(models.Video)
        form = form_cls()
        self.assertIsInstance(form.fields["tags"].widget, widgets.AdminTagWidget)
        self.assertIsInstance(form.fields["file"].widget, forms.FileInput)
        self.assertIsInstance(form.fields["focal_point_x"].widget, forms.HiddenInput)

    @override_settings(
        WAGTAILIMAGES_IMAGE_FORM_BASE="wagtail.tests.testapp.media_forms.AlternateVideoForm"
    )
    def test_overridden_base_form(self):
        self.assertIs(get_video_base_form(), AlternateVideoForm)

    @override_settings(
        WAGTAILIMAGES_IMAGE_FORM_BASE="wagtail.tests.testapp.media_forms.AlternateVideoForm"
    )
    def test_get_overridden_video_form(self):
        bases = get_video_form(models.Video).__bases__
        self.assertNotIn(BaseVideoForm, bases)
        self.assertIn(AlternateVideoForm, bases)

    @override_settings(
        WAGTAILIMAGES_IMAGE_FORM_BASE="wagtail.tests.testapp.media_forms.AlternateVideoForm"
    )
    def test_get_overridden_video_form_widgets(self):
        form_cls = get_video_form(models.Video)
        form = form_cls()
        self.assertIsInstance(form.fields["tags"].widget, OverriddenWidget)
        self.assertIsInstance(form.fields["file"].widget, OverriddenWidget)
        self.assertIsInstance(form.fields["focal_point_x"].widget, forms.HiddenInput)

        self.assertIn("form_only_field", form.fields)
        self.assertIs(form.Meta.widgets["form_only_field"], AdminDateTimeInput)
