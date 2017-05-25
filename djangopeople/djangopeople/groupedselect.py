from django import forms
from django.forms.utils import flatatt
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
# From http://www.djangosnippets.org/snippets/200/

# widget for select with optional opt groups
# modified from ticket 3442
# not sure if it's better but it doesn't force all options to be grouped

# Example:
# groceries = ((False, (('milk','milk'), (-1,'eggs'))),
#              ('fruit', ((0,'apple'), (1,'orange'))),
#              ('', (('yum','beer'), )),
#             )
# grocery_list = GroupedChoiceField(choices=groceries)

# Renders:
# <select name="grocery_list" id="id_grocery_list">
#   <option value="milk">milk</option>
#   <option value="-1">eggs</option>
#   <optgroup label="fruit">
#     <option value="0">apple</option>
#     <option value="1">orange</option>
#   </optgroup>
#   <option value="yum">beer</option>
# </select>


class GroupedSelect(forms.Select):
    def render(self, name, value, attrs=None, choices=(), renderer=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, extra_attrs={'name': name})
        output = [u'<select%s>' % flatatt(final_attrs)]
        str_value = str(value)
        for group_label, group in self.choices:
            if group_label:  # should belong to an optgroup
                group_label = str(group_label)
                output.append('<optgroup label="%s">' % escape(group_label))
            for k, v in group:
                option_value = str(k)
                option_label = str(v)
                selected_html = ((option_value == str_value) and
                                 ' selected="selected"' or '')
                output.append('<option value="%s"%s>%s</option>' % (
                    escape(option_value), selected_html,
                    escape(option_label)
                ))
            if group_label:
                output.append('</optgroup>')
        output.append('</select>')
        return mark_safe('\n'.join(output))


# field for grouped choices, handles cleaning of funky choice tuple
class GroupedChoiceField(forms.ChoiceField):
    def __init__(self, choices=(), required=True, widget=GroupedSelect,
                 label=None, initial=None, help_text=None):
        super(forms.ChoiceField, self).__init__(required, widget, label,
                                                initial, help_text)
        self.choices = choices

    def clean(self, value):
        """
        Validates that the input is in self.choices.
        """
        value = super(forms.ChoiceField, self).clean(value)
        if value in (None, ''):
            value = ''
        value = str(value)
        if value == '':
            return value
        valid_values = []
        for group_label, group in self.choices:
            valid_values += [str(k) for k, v in group]
        if value not in valid_values:
            raise forms.ValidationError(
                _('Select a valid choice. That choice is not one of the '
                  'available choices.')
            )
        return value
