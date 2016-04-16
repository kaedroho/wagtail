import json
import collections
import datetime

from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.utils import timezone

from wagtail.api.v2.tests.test_pages import TestPageDetail, TestPageListing
from wagtail.wagtailcore.models import Page

from wagtail.tests.demosite import models
from wagtail.tests.testapp.models import StreamPage

from .utils import AdminAPITestCase


def get_total_page_count():
    # Need to take away 1 as the root page is invisible over the API by default
    return Page.objects.count() - 1


class TestPageListing(AdminAPITestCase):
    fixtures = ['demosite.json']

    def get_response(self, **params):
        return self.client.get(reverse('wagtailadmin_api_v1:pages:listing'), params)

    def get_page_id_list(self, content):
        return [page['id'] for page in content['items']]


    # BASIC TESTS

    def test_basic(self):
        response = self.get_response()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-type'], 'application/json')

        # Will crash if the JSON is invalid
        content = json.loads(response.content.decode('UTF-8'))

        # Check that the meta section is there
        self.assertIn('meta', content)
        self.assertIsInstance(content['meta'], dict)

        # Check that the total count is there and correct
        self.assertIn('total_count', content['meta'])
        self.assertIsInstance(content['meta']['total_count'], int)
        self.assertEqual(content['meta']['total_count'], get_total_page_count())

        # Check that the items section is there
        self.assertIn('items', content)
        self.assertIsInstance(content['items'], list)

        # Check that each page has a meta section with type, detail_url, html_url, status and children attributes
        for page in content['items']:
            self.assertIn('meta', page)
            self.assertIsInstance(page['meta'], dict)
            self.assertEqual(set(page['meta'].keys()), {'type', 'detail_url', 'html_url', 'status', 'children', 'slug', 'first_published_at', 'latest_revision_created_at'})  # ADMINAPI CHANGE

        # Check the type info
        self.assertIsInstance(content['__types'], dict)
        self.assertEqual(set(content['__types'].keys()), {
            'demosite.EventPage',
            'demosite.StandardIndexPage',
            'demosite.PersonPage',
            'demosite.HomePage',
            'demosite.StandardPage',
            'demosite.EventIndexPage',
            'demosite.ContactPage',
            'demosite.BlogEntryPage',
            'demosite.BlogIndexPage',
        })
        self.assertEqual(set(content['__types']['demosite.EventPage'].keys()), {'verbose_name', 'verbose_name_plural'})
        self.assertEqual(content['__types']['demosite.EventPage']['verbose_name'], 'event page')
        self.assertEqual(content['__types']['demosite.EventPage']['verbose_name_plural'], 'event pages')

    def test_unpublished_pages_appear_in_list(self):  # ADMINAPI CHANGE
        total_count = get_total_page_count()

        page = models.BlogEntryPage.objects.get(id=16)
        page.unpublish()

        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        self.assertEqual(content['meta']['total_count'], total_count)

    def test_private_pages_appear_in_list(self):  # ADMINAPI CHANGE
        total_count = get_total_page_count()

        page = models.BlogIndexPage.objects.get(id=5)
        page.view_restrictions.create(password='test')

        new_total_count = get_total_page_count()
        self.assertEqual(total_count, total_count)

        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        self.assertEqual(content['meta']['total_count'], new_total_count)


    # FIELDS

    def test_fields_default(self):  # ADMINAPI CHANGE
        response = self.get_response(type='demosite.BlogEntryPage')
        content = json.loads(response.content.decode('UTF-8'))

        for page in content['items']:
            self.assertEqual(set(page.keys()), {'id', 'meta', 'title'})
            self.assertEqual(set(page['meta'].keys()), {'type', 'detail_url', 'html_url', 'children', 'status', 'slug', 'first_published_at', 'latest_revision_created_at'})

    def test_fields_parent(self):  # ADMINAPI CHANGE
        response = self.get_response(type='demosite.BlogEntryPage', fields='parent')
        content = json.loads(response.content.decode('UTF-8'))

        for page in content['items']:
            parent = page['meta']['parent']

            # All blog entry pages have the same parent
            self.assertEqual(parent, {
                'id': 5,
                'meta': {
                    'type': 'demosite.BlogIndexPage',
                    'detail_url': 'http://localhost/admin/api/v2beta/pages/5/',
                    'html_url': 'http://localhost/blog-index/',
                }
            })


    # CHILD OF FILTER

    def test_child_of_root(self):  # ADMINAPI CHANGE
        # Only return the homepage as that's the only child of the "root" node
        # in the tree. This is different to the public API which pretends the
        # homepage of the current site is the root page.
        response = self.get_response(child_of='root')
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [2])

    def test_child_of_root_doesnt_give_error(self):  # ADMINAPI CHANGE
        # Public API doesn't allow this
        response = self.get_response(child_of=1)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 200)


    # DESCENDANT OF FILTER

    def test_descendant_of_root(self):  # ADMINAPI CHANGE
        response = self.get_response(descendant_of='root')
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [2, 4, 8, 9, 5, 16, 18, 19, 6, 10, 15, 17, 21, 22, 23, 20, 13, 14, 12])

    def test_descendant_of_root_doesnt_give_error(self):  # ADMINAPI CHANGE
        # Public API doesn't allow this
        response = self.get_response(descendant_of=1)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 200)


    # HAS CHILDREN FILTER

    def test_has_children_filter(self):  # ADMINAPI CHANGE
        response = self.get_response(has_children=1)
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [2, 4, 5, 6, 21, 20])

    def test_has_children_filter_off(self):  # ADMINAPI CHANGE
        response = self.get_response(has_children=0)
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [8, 9, 16, 18, 19, 10, 15, 17, 22, 23, 13, 14, 12])

    def test_has_children_filter_invalid_integer(self):  # ADMINAPI CHANGE
        response = self.get_response(has_children=3)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "has_children must be 1 or 0"})

    def test_has_children_filter_invalid_value(self):  # ADMINAPI CHANGE
        response = self.get_response(has_children='yes')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "has_children must be 1 or 0"})


class TestAdminPageDetail(AdminAPITestCase, TestPageDetail):
    fixtures = ['demosite.json']

    def get_response(self, page_id, **params):
        return self.client.get(reverse('wagtailadmin_api_v1:pages:detail', args=(page_id, )), params)

    def test_basic(self):
        response = self.get_response(16)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-type'], 'application/json')

        # Will crash if the JSON is invalid
        content = json.loads(response.content.decode('UTF-8'))

        # Check the id field
        self.assertIn('id', content)
        self.assertEqual(content['id'], 16)

        # Check that the meta section is there
        self.assertIn('meta', content)
        self.assertIsInstance(content['meta'], dict)

        # Check the meta type
        self.assertIn('type', content['meta'])
        self.assertEqual(content['meta']['type'], 'demosite.BlogEntryPage')

        # Check the meta detail_url
        self.assertIn('detail_url', content['meta'])
        self.assertEqual(content['meta']['detail_url'], 'http://localhost/admin/api/v2beta/pages/16/')

        # Check the meta html_url
        self.assertIn('html_url', content['meta'])
        self.assertEqual(content['meta']['html_url'], 'http://localhost/blog-index/blog-post/')

        # Check the meta status
        # ADMINAPI CHANGE
        self.assertIn('status', content['meta'])
        self.assertEqual(content['meta']['status'], {
            'status': 'live',
            'live': True,
            'has_unpublished_changes': False
        })

        # Check the meta children
        # ADMINAPI CHANGE
        self.assertIn('children', content['meta'])
        self.assertEqual(content['meta']['children'], {
            'count': 0,
            'listing_url': 'http://localhost/admin/api/v2beta/pages/?child_of=16'
        })

        # Check the parent field
        self.assertIn('parent', content['meta'])
        self.assertIsInstance(content['meta']['parent'], dict)
        self.assertEqual(set(content['meta']['parent'].keys()), {'id', 'meta'})
        self.assertEqual(content['meta']['parent']['id'], 5)
        self.assertIsInstance(content['meta']['parent']['meta'], dict)
        self.assertEqual(set(content['meta']['parent']['meta'].keys()), {'type', 'detail_url', 'html_url'})
        self.assertEqual(content['meta']['parent']['meta']['type'], 'demosite.BlogIndexPage')
        self.assertEqual(content['meta']['parent']['meta']['detail_url'], 'http://localhost/admin/api/v2beta/pages/5/')
        self.assertEqual(content['meta']['parent']['meta']['html_url'], 'http://localhost/blog-index/')

        # Check that the custom fields are included
        self.assertIn('date', content)
        self.assertIn('body', content)
        self.assertIn('tags', content)
        self.assertIn('feed_image', content)
        self.assertIn('related_links', content)
        self.assertIn('carousel_items', content)

        # Check that the date was serialised properly
        self.assertEqual(content['date'], '2013-12-02')

        # Check that the tags were serialised properly
        self.assertEqual(content['tags'], ['bird', 'wagtail'])

        # Check that the feed image was serialised properly
        self.assertIsInstance(content['feed_image'], dict)
        self.assertEqual(set(content['feed_image'].keys()), {'id', 'meta'})
        self.assertEqual(content['feed_image']['id'], 7)
        self.assertIsInstance(content['feed_image']['meta'], dict)
        self.assertEqual(set(content['feed_image']['meta'].keys()), {'type', 'detail_url'})
        self.assertEqual(content['feed_image']['meta']['type'], 'wagtailimages.Image')
        self.assertEqual(content['feed_image']['meta']['detail_url'], 'http://localhost/admin/api/v2beta/images/7/')

        # Check that the child relations were serialised properly
        self.assertEqual(content['related_links'], [])
        for carousel_item in content['carousel_items']:
            self.assertEqual(set(carousel_item.keys()), {'id', 'meta', 'embed_url', 'link', 'caption', 'image'})
            self.assertEqual(set(carousel_item['meta'].keys()), {'type'})

        # Check the type info
        self.assertIsInstance(content['__types'], dict)
        self.assertEqual(set(content['__types'].keys()), {
            'demosite.BlogIndexPage',
            'demosite.BlogEntryPageCarouselItem',
            'demosite.BlogEntryPage',
            'wagtailimages.Image'
        })
        self.assertEqual(set(content['__types']['demosite.BlogIndexPage'].keys()), {'verbose_name', 'verbose_name_plural'})
        self.assertEqual(content['__types']['demosite.BlogIndexPage']['verbose_name'], 'blog index page')
        self.assertEqual(content['__types']['demosite.BlogIndexPage']['verbose_name_plural'], 'blog index pages')

    def test_field_ordering(self):
        # Need to override this as the admin API has a __types field

        response = self.get_response(16)

        # Will crash if the JSON is invalid
        content = json.loads(response.content.decode('UTF-8'))

        # Test field order
        content = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(response.content.decode('UTF-8'))
        field_order = [
            'id',
            'meta',
            'title',
            'body',
            'tags',
            'date',
            'feed_image',
            'carousel_items',
            'related_links',
            '__types',
        ]
        self.assertEqual(list(content.keys()), field_order)

    def test_meta_status_draft(self):  # ADMINAPI CHANGE
        # Unpublish the page
        Page.objects.get(id=16).unpublish()

        response = self.get_response(16)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('status', content['meta'])
        self.assertEqual(content['meta']['status'], {
            'status': 'draft',
            'live': False,
            'has_unpublished_changes': True
        })

    def test_meta_status_live_draft(self):  # ADMINAPI CHANGE
        # Save revision without republish
        Page.objects.get(id=16).save_revision()

        response = self.get_response(16)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('status', content['meta'])
        self.assertEqual(content['meta']['status'], {
            'status': 'live + draft',
            'live': True,
            'has_unpublished_changes': True
        })

    def test_meta_status_scheduled(self):  # ADMINAPI CHANGE
        # Unpublish and save revision with go live date in the future
        Page.objects.get(id=16).unpublish()
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        Page.objects.get(id=16).save_revision(approved_go_live_at=tomorrow)

        response = self.get_response(16)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('status', content['meta'])
        self.assertEqual(content['meta']['status'], {
            'status': 'scheduled',
            'live': False,
            'has_unpublished_changes': True
        })

    def test_meta_status_expired(self):  # ADMINAPI CHANGE
        # Unpublish and set expired flag
        Page.objects.get(id=16).unpublish()
        Page.objects.filter(id=16).update(expired=True)

        response = self.get_response(16)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('status', content['meta'])
        self.assertEqual(content['meta']['status'], {
            'status': 'expired',
            'live': False,
            'has_unpublished_changes': True
        })

    def test_meta_children_for_parent(self):  # ADMINAPI CHANGE
        # Homepage should have children
        response = self.get_response(2)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('children', content['meta'])
        self.assertEqual(content['meta']['children'], {
            'count': 5,
            'listing_url': 'http://localhost/admin/api/v2beta/pages/?child_of=2'
        })


class TestPageDetailWithStreamField(AdminAPITestCase):
    fixtures = ['test.json']

    def setUp(self):
        super(TestPageDetailWithStreamField, self).setUp()

        self.homepage = Page.objects.get(url_path='/home/')

    def make_stream_page(self, body):
        stream_page = StreamPage(
            title='stream page',
            slug='stream-page',
            body=body
        )
        return self.homepage.add_child(instance=stream_page)

    def test_can_fetch_streamfield_content(self):
        stream_page = self.make_stream_page('[{"type": "text", "value": "foo"}]')

        response_url = reverse('wagtailadmin_api_v1:pages:detail', args=(stream_page.id, ))
        response = self.client.get(response_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

        content = json.loads(response.content.decode('utf-8'))

        self.assertIn('id', content)
        self.assertEqual(content['id'], stream_page.id)
        self.assertIn('body', content)
        self.assertEqual(content['body'], [{'type': 'text', 'value': 'foo'}])

    def test_image_block(self):
        stream_page = self.make_stream_page('[{"type": "image", "value": 1}]')

        response_url = reverse('wagtailadmin_api_v1:pages:detail', args=(stream_page.id, ))
        response = self.client.get(response_url)
        content = json.loads(response.content.decode('utf-8'))

        # ForeignKeys in a StreamField shouldn't be translated into dictionary representation
        self.assertEqual(content['body'], [{'type': 'image', 'value': 1}])
