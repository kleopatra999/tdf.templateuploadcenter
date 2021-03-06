from Acquisition import aq_inner
from plone import api
from plone.app.layout.viewlets import ViewletBase
from plone.app.multilingual.dx import directives
from plone.app.textfield import RichText
from plone.directives import form
from plone.supermodel import model
from Products.CMFPlone.browser.search import quote_chars
from Products.Five import BrowserView
from Products.ZCTextIndex.ParseTree import ParseError
from tdf.templateuploadcenter import MessageFactory as _
from tdf.templateuploadcenter.tupproject import ITUpProject
from zope import schema


MULTISPACE = u'\u3000'.encode('utf-8')
BAD_CHARS = ('?', '-', '+', '*', MULTISPACE)


class ITUpCenter(model.Schema):

    """ An Template Upload Center for LibreOffice templates.
    """

    title = schema.TextLine(
        title=_(u"Name of the Template Center"),
    )

    description = schema.Text(
        description=_(u"Description of the Template Center"),
    )

    product_description = schema.Text(
        description=_(u"Description of the features of templates")
    )

    product_title = schema.TextLine(
        title=_(u"Template Product Name"),
        description=_(u"Name of the Template product, e.g. only Templates or LibreOffice Templates"),
    )

    available_category = schema.List(title=_(u"Available Categories"),
                                     default=['Accounting',
                                              'Agenda',
                                              'Arts',
                                              'Book',
                                              'Brochure / Pamphlet',
                                              'Budget',
                                              'Business',
                                              'Business POS',
                                              'Business Shipping',
                                              'Calendar',
                                              'Cards',
                                              'Curriculum Vitae',
                                              'CD / DVD|CD',
                                              'Certificate',
                                              'Checkbook',
                                              'Christmas',
                                              'Computer',
                                              'Conference',
                                              'E-book',
                                              'Education',
                                              'Academia',
                                              'Elementary/Secondary school panels',
                                              'Envelope'
                                              'Fax',
                                              'Genealogy',
                                              'Grocery',
                                              'Invoice',
                                              'Labels',
                                              'LibreLogo',
                                              'Letter',
                                              'Magazine',
                                              'Media',
                                              'Medical',
                                              'Memo',
                                              'Music',
                                              'Newsletter',
                                              'Notes',
                                              'Paper',
                                              'Presentation',
                                              'Recipe',
                                              'Science',
                                              'Sports',
                                              'Timeline',
                                              'Timesheet',
                                              'Trades',
                                              'To Do List',
                                              'Writer',
                                              ],
                                     value_type=schema.TextLine())

    available_licenses = schema.List(title=_(u"Available Licenses"),
                                     default=['GNU-GPL-v2 (GNU General Public License Version 2)',
                                              'GNU-GPL-v3+ (General Public License Version 3 and later)',
                                              'LGPL-v2.1 (GNU Lesser General Public License Version 2.1)',
                                              'LGPL-v3+ (GNU Lesser General Public License Version 3 and later)',
                                              'BSD (BSD License (revised))',
                                              'MPL-v1.1 (Mozilla Public License Version 1.1)',
                                              'MPL-v2.0+ (Mozilla Public License Version 2.0 or later)',
                                              'CC-by-sa-v3 (Creative Commons Attribution-ShareAlike 3.0)',
                                              'CC-BY-SA-v4 (Creative Commons Attribution-ShareAlike 4.0 International)',
                                              'AL-v2 (Apache License Version 2.0)',
                                              'Public Domain',
                                              'OSI (Other OSI Approved)'],
                                     value_type=schema.TextLine())

    available_versions = schema.List(title=_(u"Available Versions"),
                                     default=['LibreOffice 3.3',
                                              'LibreOffice 3.4',
                                              'LibreOffice 3.5',
                                              'LibreOffice 3.6',
                                              'LibreOffice 4.0',
                                              'LibreOffice 4.1',
                                              'LibreOffice 4.2',
                                              'LibreOffice 4.3',
                                              'LibreOffice 4.4',
                                              'LibreOffice 5.0',
                                              'LibreOffice 5.1',
                                              'LibreOffice 5.2',
                                              'LibreOffice 5.3'],
                                     value_type=schema.TextLine())

    available_platforms = schema.List(title=_(u"Available Platforms"),
                                      default=['All platforms',
                                               'Linux',
                                               'Linux-x64',
                                               'Mac OS X',
                                               'Windows',
                                               'BSD',
                                               'UNIX (other)'],
                                      value_type=schema.TextLine())

    form.primary('install_instructions')
    install_instructions = RichText(
        title=_(u"Template Installation Instructions"),
        description=_(u"Please fill in the install instructions"),
        required=False
    )

    form.primary('reporting_bugs')
    reporting_bugs = RichText(
        title=_(u"Instruction how to report Bugs"),
        required=False
    )

    title_legaldisclaimer = schema.TextLine(
        title=_(u"Title for Legal Disclaimer and Limitations"),
        default=_(u"Legal Disclaimer and Limitations"),
        required=False
    )

    legal_disclaimer = schema.Text(
        title=_(u"Text of the Legal Disclaimer and Limitations"),
        description=_(u"Enter the text of the legal disclaimer and limitations that should be displayed "
                      u"to the project creator and should be accepted by the owner of the project."),
        default=_(u"Fill in the legal disclaimer, that had to be accepted by the project owner"),
        required=False
    )

    title_legaldownloaddisclaimer = schema.TextLine(
        title=_(u"Title of the Legal Disclaimer and Limitations for Downloads"),
        default=_(u"Legal Disclaimer and Limitations for Downloads"),
        required=False
    )

    form.primary('legal_downloaddisclaimer')
    legal_downloaddisclaimer = RichText(
        title=_(u"Text of the Legal Disclaimer and Limitations for Downlaods"),
        description=_(u"Enter any legal disclaimer and limitations for downloads that should "
                      u"appear on each page for dowloadable files."),
        default=_(u"Fill in the text for the legal download disclaimer"),
        required=False
    )


def notifyAboutNewProject(tupproject, event):
    api.portal.send_email(
        recipient="templates@libreoffice.org",
        subject="A Project with the title %s was added" % (tupproject.title),
        body="A member added a new project"
    )

directives.languageindependent('available_category')
directives.languageindependent('available_licenses')
directives.languageindependent('available_versions')
directives.languageindependent('available_platforms')

# Views


class TUpCenterView(BrowserView):

    def tupprojects(self):
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')

        return catalog(object_provides=ITUpProject.__identifier__,
                       path='/'.join(context.getPhysicalPath()),
                       sort_order='sortable_title')

    def get_latest_program_release(self):
        """Get the latest version from the vocabulary. This only
        goes by string sorting so would need to be reworked if the
        LibreOffice versions dramatically changed"""

        versions = list(self.context.available_versions)
        versions.sort(reverse=True)
        return versions[0]

    def category_name(self):
        category = list(self.context.available_category)
        return category

    def tupproject_count(self):
        """Return number of projects
        """
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')

        return len(catalog(portal_type='tdf.templateuploadcenter.tupproject'))

    def tuprelease_count(self):
        """Return number of downloadable files
        """
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')

        return len(catalog(portal_type='tdf.templateuploadcenter.tuprelease'))

    def get_most_popular_products(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        sort_on = 'positive_ratings'
        contentFilter = {
                         'sort_on': sort_on,
                         'sort_order': 'reverse',
                         'review_state': 'published',
                         'portal_type': 'tdf.templateuploadcenter.tupproject'}
        return catalog(**contentFilter)

    def get_newest_products(self):
        self.catalog = api.portal.get_tool(name='portal_catalog')
        sort_on = 'created'
        contentFilter = {
                          'sort_on': sort_on,
                          'sort_order': 'reverse',
                          'review_state': 'published',
                          'portal_type': 'tdf.templateuploadcenter.tupproject'}

        results = self.catalog(**contentFilter)

        return results

    def get_products(self, category, version, sort_on, SearchableText=None):
        self.catalog = api.portal.get_tool(name='portal_catalog')
        # sort_on = 'positive_ratings'
        if SearchableText:
            SearchableText = self.munge_search_term(SearchableText)

        contentFilter = {'sort_on': sort_on,
                         'SearchableText': SearchableText,
                         'sort_order': 'reverse',
                         'portal_type': 'tdf.templateuploadcenter.tupproject'}
        if version != 'any':
            # We ask to the indexed value on the project (aggregated from
            # releases on creation/modify/delete of releases)
            contentFilter['releases_compat_versions'] = version

        if category:
            contentFilter['getCategories'] = category

        try:
            return self.catalog(**contentFilter)
        except ParseError:
            return []

    def munge_search_term(self, q):
        for char in BAD_CHARS:
            q = q.replace(char, ' ')
        r = q.split()
        r = " AND ".join(r)
        r = quote_chars(r) + '*'
        return r

    def show_search_form(self):
        return 'getCategories' in self.request.environ['QUERY_STRING']


class TUpCenterOwnProjectsViewlet(ViewletBase):

    def get_results(self):
        current_user = api.user.get_current()
        pc = api.portal.get_tool('portal_catalog')
        return pc.portal_catalog(
            portal_type='tdf.templateuploadcenter.tupproject',
            sort_on='Date',
            sort_order='reverse',
            Creator=str(current_user))
