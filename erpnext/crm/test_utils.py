import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today

from erpnext.crm.utils import get_open_activities


class TestCRMUtils(IntegrationTestCase):
	def test_get_open_activities_sorted_by_date(self):
		lead = frappe.get_doc(
			{
				"doctype": "Lead",
				"first_name": "Activity",
				"last_name": "Order",
				"email_id": "activity_order@example.com",
			}
		).insert()

		later_todo = frappe.get_doc(
			{
				"doctype": "ToDo",
				"description": "Later task",
				"date": add_days(today(), 10),
				"reference_type": "Lead",
				"reference_name": lead.name,
			}
		).insert()

		earlier_todo = frappe.get_doc(
			{
				"doctype": "ToDo",
				"description": "Earlier task",
				"date": add_days(today(), 1),
				"reference_type": "Lead",
				"reference_name": lead.name,
			}
		).insert()

		later_event = _create_event("Later meeting", add_days(today(), 10), "Lead", lead.name)
		earlier_event = _create_event("Earlier meeting", add_days(today(), 1), "Lead", lead.name)

		activities = get_open_activities("Lead", lead.name)

		self.assertEqual([task.name for task in activities["tasks"]], [earlier_todo.name, later_todo.name])
		self.assertEqual(
			[event.name for event in activities["events"]], [earlier_event.name, later_event.name]
		)


def _create_event(subject, starts_on, reference_type, reference_name):
	event = frappe.new_doc("Event")
	event.subject = subject
	event.starts_on = starts_on
	event.event_type = "Private"
	event.all_day = 1
	event.append(
		"event_participants", {"reference_doctype": reference_type, "reference_docname": reference_name}
	)
	event.insert()
	return event
