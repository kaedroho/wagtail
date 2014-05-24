# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'QueryDailyHits', fields ['query', 'date']
        db.delete_unique(u'wagtaileditorspicks_querydailyhits', ['query_id', 'date'])

        # Deleting model 'Query'
        db.delete_table(u'wagtaileditorspicks_query')

        # Deleting field 'EditorsPick.query'
        db.delete_column(u'wagtaileditorspicks_editorspick', 'query_id')

        # Deleting field 'QueryDailyHits.query'
        db.delete_column(u'wagtaileditorspicks_querydailyhits', 'query_id')

        # Adding unique constraint on 'QueryDailyHits', fields ['query_string', 'date']
        db.create_unique(u'wagtaileditorspicks_querydailyhits', ['query_string', 'date'])


    def backwards(self, orm):
        # Removing unique constraint on 'QueryDailyHits', fields ['query_string', 'date']
        db.delete_unique(u'wagtaileditorspicks_querydailyhits', ['query_string', 'date'])

        # Adding model 'Query'
        db.create_table(u'wagtaileditorspicks_query', (
            ('query_string', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'wagtaileditorspicks', ['Query'])


        # User chose to not deal with backwards NULL issues for 'EditorsPick.query'
        raise RuntimeError("Cannot reverse this migration. 'EditorsPick.query' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'EditorsPick.query'
        db.add_column(u'wagtaileditorspicks_editorspick', 'query',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='editors_picks', to=orm['wagtaileditorspicks.Query']),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'QueryDailyHits.query'
        raise RuntimeError("Cannot reverse this migration. 'QueryDailyHits.query' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'QueryDailyHits.query'
        db.add_column(u'wagtaileditorspicks_querydailyhits', 'query',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='daily_hits', to=orm['wagtaileditorspicks.Query']),
                      keep_default=False)

        # Adding unique constraint on 'QueryDailyHits', fields ['query', 'date']
        db.create_unique(u'wagtaileditorspicks_querydailyhits', ['query_id', 'date'])


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'wagtailcore.page': {
            'Meta': {'object_name': 'Page'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pages'", 'to': u"orm['contenttypes.ContentType']"}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'has_unpublished_changes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'live': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_pages'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'search_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'seo_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'show_in_menus': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url_path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'wagtaileditorspicks.editorspick': {
            'Meta': {'ordering': "('sort_order',)", 'object_name': 'EditorsPick'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['wagtailcore.Page']"}),
            'query_string': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'wagtaileditorspicks.querydailyhits': {
            'Meta': {'unique_together': "(('query_string', 'date'),)", 'object_name': 'QueryDailyHits'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'hits': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'query_string': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['wagtaileditorspicks']