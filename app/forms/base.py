# -*- coding: utf-8 -*-

from flask_wtf import Form
from flask import flash


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
            flash("{} created and saved.".format(getattr(instance, "friendly_name", instance.__class__.__name__)), "info")
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
