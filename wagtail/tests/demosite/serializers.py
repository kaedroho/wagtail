from __future__ import absolute_import, unicode_literals

from rest_framework import serializers

from wagtail.api.v2.serializers import PageSerializer
from wagtail.wagtailimages.api.v2.serializers import ImageSerializer
from wagtail.wagtailimages.api.fields import ImageRenditionField

from . import models


# ABSTRACT SERIALIZERS
# =============================

class AbstractLinkFieldsSerializer(serializers.ModelSerializer):

    class Meta:
        abstract = True
        fields = ['link']


class AbstractRelatedLinkSerializer(AbstractLinkFieldsSerializer):

    class Meta(AbstractLinkFieldsSerializer.Meta):
        abstract = True
        fields = ['title'] + AbstractLinkFieldsSerializer.Meta.fields


class AbstractCarouselItemSerializer(AbstractLinkFieldsSerializer):
    #image = ImageSerializer()
    image_fullwidth_rendition = ImageRenditionField('width-1000', source='image')

    class Meta(AbstractLinkFieldsSerializer.Meta):
        abstract = True
        fields = ['image', 'image_fullwidth_rendition', 'embed_url', 'caption'] + AbstractLinkFieldsSerializer.Meta.fields


class ContactFieldsSerializerMixin(serializers.ModelSerializer):

    class Meta:
        abstract = True
        fields = [
            'telephone',
            'email',
            'address_1',
            'address_2',
            'city',
            'country',
            'post_code',
        ]


# PAGE SERIALIZERS
# =============================

# Home page

class HomePageCarouselItemSerializer(AbstractCarouselItemSerializer):

    class Meta(AbstractCarouselItemSerializer.Meta):
        model = models.HomePageCarouselItem


class HomePageRelatedLinkSerializer(AbstractRelatedLinkSerializer):

    class Meta(AbstractRelatedLinkSerializer.Meta):
        model = models.HomePageRelatedLink


class HomePageSerializer(PageSerializer):
    carousel_items = HomePageCarouselItemSerializer(many=True)
    related_links = HomePageRelatedLinkSerializer(many=True)

    class Meta(PageSerializer.Meta):
        model = models.HomePage
        fields = PageSerializer.Meta.fields + [
            'body',
            'carousel_items',
            'related_links',
        ]


# Standard pages

class StandardPageCarouselItemSerializer(AbstractCarouselItemSerializer):

    class Meta(AbstractCarouselItemSerializer.Meta):
        model = models.StandardPageCarouselItem


class StandardPageRelatedLinkSerializer(AbstractRelatedLinkSerializer):

    class Meta(AbstractRelatedLinkSerializer.Meta):
        model = models.StandardPageRelatedLink


class StandardPageSerializer(PageSerializer):
    #feed_image = ImageSerializer()
    feed_image_thumbnail_rendition = ImageRenditionField('fill-100x100', source='feed_image')
    carousel_items = StandardPageCarouselItemSerializer(many=True)
    related_links = StandardPageRelatedLinkSerializer(many=True)

    class Meta(PageSerializer.Meta):
        model = models.StandardPage
        fields = PageSerializer.Meta.fields + [
            'intro',
            'body',
            'feed_image',
            'feed_image_thumbnail_rendition',
            'carousel_items',
            'related_links',
        ]


class StandardIndexPageRelatedLinkSerializer(AbstractRelatedLinkSerializer):

    class Meta(AbstractRelatedLinkSerializer.Meta):
        model = models.StandardIndexPageRelatedLink


class StandardIndexPageSerializer(PageSerializer):
    #feed_image = ImageSerializer()
    feed_image_thumbnail_rendition = ImageRenditionField('fill-100x100', source='feed_image')
    related_links = StandardIndexPageRelatedLinkSerializer(many=True)

    class Meta(PageSerializer.Meta):
        model = models.StandardIndexPage
        fields = PageSerializer.Meta.fields + [
            'intro',
            'feed_image',
            'feed_image_thumbnail_rendition',
            'related_links',
        ]


# Blog pages

class BlogEntryPageCarouselItemSerializer(AbstractCarouselItemSerializer):

    class Meta(AbstractCarouselItemSerializer.Meta):
        model = models.BlogEntryPageCarouselItem


class BlogEntryPageRelatedLinkSerializer(AbstractRelatedLinkSerializer):

    class Meta(AbstractRelatedLinkSerializer.Meta):
        model = models.BlogEntryPageRelatedLink


class BlogEntryPageSerializer(PageSerializer):
    # TODO: tags?
    #feed_image = ImageSerializer()
    feed_image_thumbnail_rendition = ImageRenditionField('fill-100x100', source='feed_image')
    carousel_items = BlogEntryPageCarouselItemSerializer(many=True)
    related_links = BlogEntryPageRelatedLinkSerializer(many=True)

    class Meta(PageSerializer.Meta):
        model = models.BlogEntryPage
        fields = PageSerializer.Meta.fields + [
            'body',
            'tags',
            'date',
            'feed_image',
            'carousel_items',
            'related_links',
        ]


class BlogIndexPageRelatedLinkSerializer(AbstractRelatedLinkSerializer):

    class Meta(AbstractRelatedLinkSerializer.Meta):
        model = models.BlogIndexPageRelatedLink


class BlogIndexPageSerializer(PageSerializer):
    related_links = BlogIndexPageRelatedLinkSerializer(many=True)

    class Meta(PageSerializer.Meta):
        model = models.BlogIndexPage
        fields = PageSerializer.Meta.fields + [
            'intro',
            'related_links',
        ]


# Events pages

class EventPageCarouselItemSerializer(AbstractCarouselItemSerializer):

    class Meta(AbstractCarouselItemSerializer.Meta):
        model = models.EventPageCarouselItem


class EventPageRelatedLinkSerializer(AbstractRelatedLinkSerializer):

    class Meta(AbstractRelatedLinkSerializer.Meta):
        model = models.EventPageRelatedLink


class EventPageSpeakerSerializer(serializers.ModelSerializer):
    #image = ImageSerializer()
    image_thumbnail_rendition = ImageRenditionField('fill-100x100', source='image')

    class Meta:
        model = models.EventPageSpeaker

        fields = [
            'first_name',
            'last_name',
            'image',
            'image_thumbnail_rendition',
        ]


class EventPageSerializer(PageSerializer):
    # TODO: body (streamfield)?
    #feed_image = ImageSerializer()
    feed_image_thumbnail_rendition = ImageRenditionField('fill-100x100', source='feed_image')
    carousel_items = EventPageCarouselItemSerializer(many=True)
    related_links = EventPageRelatedLinkSerializer(many=True)
    speakers = EventPageSpeakerSerializer(many=True)

    class Meta(PageSerializer.Meta):
        model = models.EventPage
        fields = PageSerializer.Meta.fields + [
            'date_from',
            'date_to',
            'time_from',
            'time_to',
            'audience',
            'location',
            'body',
            'cost',
            'signup_link',
            'feed_image',
            'feed_image_thumbnail_rendition',
            'carousel_items',
            'related_links',
            'speakers',
        ]


class EventIndexPageRelatedLinkSerializer(AbstractRelatedLinkSerializer):

    class Meta(AbstractRelatedLinkSerializer.Meta):
        model = models.EventIndexPageRelatedLink


class EventIndexPageSerializer(PageSerializer):
    related_links = EventIndexPageRelatedLinkSerializer(many=True)

    class Meta(PageSerializer.Meta):
        model = models.EventIndexPage
        fields = PageSerializer.Meta.fields + [
            'intro',
            'related_links',
        ]


# Person page

class PersonPageRelatedLinkSerializer(AbstractRelatedLinkSerializer):

    class Meta(AbstractRelatedLinkSerializer.Meta):
        model = models.PersonPageRelatedLink


class PersonPageSerializer(ContactFieldsSerializerMixin, PageSerializer):
    #image = ImageSerializer()
    image_thumbnail_rendition = ImageRenditionField('fill-100x100', source='image')
    #feed_image = ImageSerializer()
    feed_image_thumbnail_rendition = ImageRenditionField('fill-100x100', source='feed_image')
    related_links = PersonPageRelatedLinkSerializer(many=True)

    class Meta(PageSerializer.Meta):
        model = models.PersonPage
        fields = PageSerializer.Meta.fields + [
            'first_name',
            'last_name',
            'intro',
            'biography',
            'image',
            'feed_image',
            'related_links',
        ] + ContactFieldsSerializerMixin.Meta.fields


# Contact page

class ContactPageSerializer(ContactFieldsSerializerMixin, PageSerializer):
    #feed_image = ImageSerializer()
    feed_image_thumbnail_rendition = ImageRenditionField('fill-100x100', source='feed_image')

    class Meta(PageSerializer.Meta):
        model = models.ContactPage
        fields = PageSerializer.Meta.fields + [
            'body',
            'feed_image',
        ] + ContactFieldsSerializerMixin.Meta.fields
