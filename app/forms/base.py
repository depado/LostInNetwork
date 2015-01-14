# -*- coding: utf-8 -*-

from flask_wtf import Form
from flask import flash

from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField


class CustomForm(Form):

    def has_been_submitted(self, request):
        """
        Returns whether it was this form or not that was submitted.

        :param request: The flask request of the route
        :return: True if form has been submitted, False otherwise
        """
        return request.form['btn'] == "{}save-btn".format(getattr(self, "_prefix"))

    def push_new(self, model):
        """
        Automatically create the object and save it from the data in the form.
        Automatic rollback of the database in case of error.

        :param model: The model associated to the form.
        """
        instance = model()
        self.populate_obj(instance)
        if instance.save():
            flash("{} created and saved.".format(getattr(instance, "friendly_name", instance.__class__.__name__)),
                  "info")
        else:
            flash("Something went wrong.", "error")

    def push_modified(self, request, obj):
        """
        Push a modified object to the database.
        The condition is used to determine if it's a many-to-many field. As we don't handle those on the front-end,
        it will totally mess-up the data. As those fields aren't displayed, they are submitted empty.
        """
        for field in self._fields:
            if type(self._fields[field]) is QuerySelectMultipleField:
                del self[field]
        self.populate_obj(obj)
        if obj.save():
            flash(
                "{} saved.".format(getattr(obj, "friendly_name", obj.__class__.__name__)),
                "info"
            )
        else:
            flash("Something went wrong.", "error")

    def chain_push_new(self, request, model):
        """
        Validates that the form has been submitted, validates it, and push a new instance of model in case of success.
        :param request: The flask request of the route
        :param model: The model associated with the form
        """
        if self.has_been_submitted(request):
            if self.validate_on_submit():
                self.push_new(model)

    def chain_push_modified(self, request, model, obj):
        """
        Validates that the form has been sumitted, validates it, and modifies the instance given in parameter.
        :param request: The flask request
        :param model: The model associated to the form
        :param obj: THe instance that should be modified
        """
        if self.has_been_submitted(request):
            if self.validate_on_submit():
                self.push_modified(model, obj)
