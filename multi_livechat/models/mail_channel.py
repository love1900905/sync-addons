# Copyright 2021 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
from odoo import api, models

ODOO_CHANNEL_TYPES = ["chat", "channel", "livechat"]


class MailChannel(models.Model):
    _inherit = "mail.channel"

    def _compute_is_chat(self):
        super(MailChannel, self)._compute_is_chat()
        for record in self:
            if record.channel_type not in ODOO_CHANNEL_TYPES:
                record.is_chat = True

    @api.model
    def channel_fetch_slot(self):
        values = super(MailChannel, self).channel_fetch_slot()
        domain = [("channel_type", "not in", ODOO_CHANNEL_TYPES)]
        # TODO: we show all unarchived channels, which is not a good solution
        # for intensive chat support. Commented code below is how it works in
        # original Odoo Livechat: it unpins chats after some time of inactivity.
        # See also a note in README.

        # pinned_channels = self.env['mail.channel.partner'].search([('partner_id', '=', self.env.user.partner_id.id), ('is_pinned', '=', True)]).mapped('channel_id')
        # domain += [('id', 'in', pinned_channels.ids)]
        channel_infos = self.search(domain).channel_info()
        for info in channel_infos:
            key = info["channel_type"]
            values.setdefault(key, [])
            values[key].append(info)
        return values

    @api.model
    def multi_livechat_info(self):
        field = self.env["mail.channel"]._fields["channel_type"]
        return {
            "channel_types": {
                key: value
                for key, value in field.selection
                if key not in ODOO_CHANNEL_TYPES
            }
        }
