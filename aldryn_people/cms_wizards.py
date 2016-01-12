# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import transaction
from django.utils.translation import ugettext_lazy as _, ugettext

from cms.wizards.wizard_pool import wizard_pool
from cms.wizards.wizard_base import Wizard
from cms.wizards.forms import BaseFormMixin

from parler.forms import TranslatableModelForm
from reversion import create_revision, set_user, set_comment

from .models import Group, Person


def has_published_apphook():
    """
    Returns a list of app_configs that are attached to a published page.
    """
    try:
        reverse('aldryn_people:group-list')
        return True
    except NoReverseMatch:
        pass
    return False


class BasePeopleWizard(Wizard):
    """
    Only return a success URL if we can actually use it.
    """
    def get_success_url(self, **kwargs):
        if has_published_apphook():
            return super(BasePeopleWizard, self).get_success_url(**kwargs)
        else:
            return None


class PeoplePersonWizard(BasePeopleWizard):

    def user_has_add_permission(self, user, **kwargs):
        """
        Return True if the current user has permission to add a person.
        :param user: The current user
        :param kwargs: Ignored here
        :return: True if user has add permission, else False
        """
        if user.is_superuser or user.has_perm("aldryn_people.add_person"):
            return True
        return False


class PeopleGroupWizard(BasePeopleWizard):

    def user_has_add_permission(self, user, **kwargs):
        """
        Return True if the current user has permission to add a group.
        :param user: The current user
        :param kwargs: Ignored here
        :return: True if user has add permission, else False
        """
        if user.is_superuser or user.has_perm("aldryn_people.add_group"):
            return True
        return False


class CreatePeoplePersonForm(BaseFormMixin, TranslatableModelForm):
    class Meta:
        model = Person
        fields = ['name', 'function', 'description', 'phone', 'mobile',
                  'email', 'website', 'groups']

    def save(self, commit=True):
        """
        Ensure we create a revision for reversion.
        """
        person = super(CreatePeoplePersonForm, self).save(commit=False)

        # Ensure we make an initial revision
        with transaction.atomic():
            with create_revision():
                person.save()
                if self.user:
                    set_user(self.user)
                set_comment(ugettext("Initial version."))

        return person


class CreatePeopleGroupForm(BaseFormMixin, TranslatableModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'address', 'postal_code', 'city',
                  'phone', 'email', 'website']

    def save(self, commit=True):
        """
        Ensure we create a revision for reversion.
        """
        group = super(CreatePeopleGroupForm, self).save(commit=False)

        # Ensure we make an initial revision
        with transaction.atomic():
            with create_revision():
                group.save()
                if self.user:
                    set_user(self.user)
                set_comment(ugettext("Initial version."))

        return group


people_person_wizard = PeoplePersonWizard(
    title=_('New person'),
    weight=300,
    form=CreatePeoplePersonForm,
    description=_("Create a new person.")
)

wizard_pool.register(people_person_wizard)


people_group_wizard = PeopleGroupWizard(
    title=_('New group'),
    weight=300,
    form=CreatePeopleGroupForm,
    description=_("Create a new group.")
)

# Disabling the group wizard by default. To enable, create a file
# cms_wizards.py in your project and add the following lines:

# from cms.wizards.wizard_pool import wizard_pool
# from aldryn_people.cms_wizards import people_group_wizard
#
#  wizard_pool.register(people_group_wizard)