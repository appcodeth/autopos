from odoo import models, fields, api


class CarBrand(models.Model):
    """
    define car brand e.g. Toyota, Honda, Nissan etc.
    """
    _name = 'autopos.car_brand'
    _rec_name = 'name'
    name = fields.Char('Name', required=True)


class CarModel(models.Model):
    """
    define car model e.g. Civic, Accord, Altis etc.
    """
    _name = 'autopos.car_model'
    _rec_name = 'name'
    name = fields.Char('Name', required=True)
    year = fields.Char('Year')
    description = fields.Text('Description')
    brand_id = fields.Many2one('autopos.car_brand', string='Brand')


class CarType(models.Model):
    """
    define car type e.g. Truck, Van, Motorcycles etc.
    """
    _name = 'autopos.car_type'
    _rec_name = 'name'
    name = fields.Char('Name', required=True)


class CarColor(models.Model):
    """
    define car colors e.g. White, Black, Blue etc.
    """
    _name = 'autopos.car_color'
    _rec_name = 'name'
    name = fields.Char('Name', required=True)


class Car(models.Model):
    """
    define the car data
    """
    _name = 'autopos.car'
    _rec_name = 'name'
    name = fields.Char('Name', required=True)
    reg_name = fields.Char('Reg Name')
    image = fields.Image('Image')
    brand_id = fields.Many2one('autopos.car_brand', string='Brand')
    model_id = fields.Many2one('autopos.car_model', string='Model')
    type_id = fields.Many2one('autopos.car_type', string='Type')
    color_id = fields.Many2one('autopos.car_color', string='Color')
    customer_id = fields.Many2one('autopos.customer', string='Customer', ondelete='cascade')
