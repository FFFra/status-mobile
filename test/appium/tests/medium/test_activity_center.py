import pytest

from tests import marks, run_in_parallel
from tests.base_test_case import MultipleSharedDeviceTestCase, create_shared_drivers
from views.sign_in_view import SignInView


@pytest.mark.xdist_group(name="new_two_2")
@marks.new_ui_critical
class TestActivityCenterContactRequestMultipleDevicePR(MultipleSharedDeviceTestCase):

    def prepare_devices(self):
        self.drivers, self.loop = create_shared_drivers(2)
        self.device_1, self.device_2 = SignInView(self.drivers[0]), SignInView(self.drivers[1])
        self.username_1, self.username_2 = 'sender', 'receiver'
        self.loop.run_until_complete(run_in_parallel(((self.device_1.create_user, {'enable_notifications': True,
                                                                                   'username': self.username_1}),
                                                      (self.device_2.create_user, {'username': self.username_2}))))
        self.homes = self.home_1, self.home_2 = self.device_1.get_home_view(), self.device_2.get_home_view()
        self.profile_1, self.profile_2 = self.home_1.get_profile_view(), self.home_2.get_profile_view()
        self.public_key_1, self.public_key_2 = (home.get_public_key() for home in self.homes)
        [home.click_system_back_button_until_element_is_shown() for home in self.homes]
        [home.chats_tab.click() for home in self.homes]

    @marks.testrail_id(702850)
    def test_activity_center_contact_request_decline(self):
        self.device_1.put_app_to_background()
        self.device_2.just_fyi('Device2 sends a contact request to Device1 via Paste button and check user details')
        self.home_2.driver.set_clipboard_text(self.public_key_1)
        self.home_2.new_chat_button.click_until_presence_of_element(self.home_2.add_a_contact_chat_bottom_sheet_button)
        self.home_2.add_a_contact_chat_bottom_sheet_button.click()
        self.home_2.element_by_translation_id("paste").click()
        self.home_2.element_by_translation_id("user-found").wait_for_visibility_of_element(10)
        # TODO: Blocked by 15500
        # if not self.home_2.element_by_text(self.username_1).is_element_displayed():
        #     self.errors.append("Username is not shown on 'Add contact' page after entering valid public key")
        chat = self.home_2.get_chat_view()

        chat.view_profile_new_contact_button.click_until_presence_of_element(chat.profile_block_contact_button)
        chat.profile_add_to_contacts_button.click()
        self.home_2.click_system_back_button_until_element_is_shown()

        self.device_1.just_fyi("Device 1: check there is no PN when receiving new message to activity centre")
        self.device_1.open_notification_bar()
        if self.home_1.element_by_text_part("Please add me to your contacts").is_element_displayed():
            self.errors.append("Push notification with text was received for new message in activity centre")
        self.device_1.click_system_back_button(2)

        self.device_1.just_fyi('Device1 verifies pending contact request')
        self.home_1.contacts_tab.click()
        for indicator in (self.home_1.notifications_unread_badge, self.home_1.contact_new_badge):
            if not indicator.is_element_displayed():
                self.errors.append("Unread indicator on contacts tab or on activity center is not shown for incoming CR!")
        if self.home_1.pending_contact_request_text.text != '1':
            self.errors.append("The amount of contact requests is not shown for incoming CR!")

        self.device_1.just_fyi('Device1 declines pending contact request')
        self.home_1.handle_contact_request(username=self.username_2, action='decline')
        for indicator in (self.home_1.notifications_unread_badge, self.home_1.contact_new_badge, self.home_1.pending_contact_request_text):
            if indicator.is_element_displayed():
                self.errors.append("Unread indicator on contacts tab or on activity center is shown after declining contact request!")

        self.device_1.just_fyi("Check that it is still pending contact after declining on sender device")
        self.home_2.jump_to_messages_home()
        self.home_2.open_activity_center_button.click()
        self.home_2.activity_unread_filter_button.click()
        activity_center_element = self.home_2.get_element_from_activity_center_view(self.username_1)
        if activity_center_element.message_body.text != self.home_2.get_translation_by_key("add-me-to-your-contacts"):
            self.errors.append("Pending contact request is not shown on unread notification element on Activity center!,"
                               " actual is '%s'" % activity_center_element.message_body.text)
        self.home_2.close_activity_centre.click()

        self.errors.verify_no_errors()

    @marks.testrail_id(702851)
    def test_activity_center_contact_request_accept_swipe_mark_all_as_read(self):
        self.device_2.just_fyi('Device2 re-sends a contact request to Device1')
        self.home_2.add_contact(self.public_key_1, remove_from_contacts=True)

        self.device_1.just_fyi('Device1 accepts pending contact request by swiping')
        self.home_1.chats_tab.click()
        self.home_1.notifications_unread_badge.wait_for_visibility_of_element(30)
        self.home_1.open_activity_center_button.click()

        self.home_1.just_fyi("Mark all as read")
        cr_element = self.home_1.get_element_from_activity_center_view(self.username_2)
        self.home_1.more_options_activity_button.click()
        self.home_1.mark_all_read_activity_button.click()
        if cr_element.is_element_displayed():
            self.errors.append("Contact request is still shown in activity centre after marking all messages as read!")

        self.home_1.just_fyi("Check that can accept contact request from read notifications")
        self.home_1.activity_unread_filter_button.click()
        cr_element.swipe_right_on_element()
        self.home_1.activity_notification_swipe_button.click()
        self.home_1.close_activity_centre.click()
        self.home_1.contacts_tab.click()
        if not self.home_1.contact_details(username=self.username_2).is_element_displayed(20):
            self.errors.append("Contact was not added to contact list after accepting contact request (as receiver)")

        self.device_2.just_fyi('Device1 check that contact appeared in contact list mutually')
        self.home_2.chats_tab.click()
        self.home_2.contacts_tab.click()
        if not self.home_2.contact_details(username=self.username_1).is_element_displayed(20):
            self.errors.append("Contact was not added to contact list after accepting contact request (as sender)")

        self.errors.verify_no_errors()


@pytest.mark.xdist_group(name="new_one_3")
@marks.new_ui_critical
class TestActivityMultipleDevicePR(MultipleSharedDeviceTestCase):

    def prepare_devices(self):
        self.drivers, self.loop = create_shared_drivers(2)
        self.device_1, self.device_2 = SignInView(self.drivers[0]), SignInView(self.drivers[1])
        self.username_1, self.username_2 = 'user1', 'user2'
        self.loop.run_until_complete(
            run_in_parallel(((self.device_1.create_user, {'username': self.username_1}),
                             (self.device_2.create_user, {'username': self.username_2}))))
        self.homes = self.home_1, self.home_2 = self.device_1.get_home_view(), self.device_2.get_home_view()
        self.profile_1, self.profile_2 = self.home_1.get_profile_view(), self.home_2.get_profile_view()
        self.public_key_2 = self.home_2.get_public_key()
        self.home_2.click_system_back_button_until_element_is_shown()
        [home.chats_tab.click() for home in self.homes]

        self.home_1.add_contact(self.public_key_2)
        self.home_2.handle_contact_request(self.username_1)
        self.text_message = 'hello'
        self.one_to_one_message = 'one-t-one message'

        self.home_2.just_fyi("Send message to contact (need for jump to) test")
        self.chat_1 = self.home_1.get_chat(self.username_2).click()
        self.chat_1.send_message(self.one_to_one_message)
        self.chat_2 = self.home_2.get_chat(self.username_1).click()
        self.chat_2.send_message(self.text_message)
        [home.click_system_back_button_until_element_is_shown() for home in self.homes]

        self.home_1.just_fyi("Open community to message")
        self.home_1.communities_tab.click()
        self.community_name = self.home_1.get_random_chat_name()
        self.channel_name = 'general'
        self.home_1.create_community(name=self.community_name, description='community to test', require_approval=False)
        self.channel_1 = self.home_1.get_to_community_channel_from_home(self.community_name)
        self.channel_1.send_message(self.text_message)

        self.community_1, self.community_2 = self.home_1.get_community_view(), self.home_2.get_community_view()
        self.community_1.send_invite_to_community(self.community_name, self.username_2)
        self.home_1.get_to_community_channel_from_home(self.community_name)

        self.chat_2 = self.home_2.get_chat(self.username_1).click()
        self.chat_2.element_by_text_part('View').click()
        self.community_2.join_community()
        self.channel_2 = self.community_2.get_channel(self.channel_name).click()

    @marks.testrail_id(702936)
    def test_navigation_jump_to(self):
        self.community_1.just_fyi("Check Jump to screen and redirect on tap")
        self.community_1.jump_to_button.click()
        for card in (self.community_name, self.username_2):
            if not self.community_1.element_by_text_part(card).is_element_displayed(20):
                self.errors.append("Card %s is not shown on Jump to screen!" % card)
        self.community_1.element_by_translation_id("community-channel").click()
        if not self.channel_1.chat_element_by_text(self.text_message).is_element_displayed(20):
            self.errors.append("User was not redirected to community channel after tapping on community channel card!")
        self.channel_1.click_system_back_button()
        self.community_1.jump_to_button.click()
        self.community_1.element_by_text_part(self.username_2).click()
        if not self.chat_1.chat_element_by_text(self.one_to_one_message).is_element_displayed(20):
            self.errors.append("User was not redirected to 1-1 chat after tapping card!")

        self.errors.verify_no_errors()

    @marks.testrail_id(702947)
    def test_activity_center_reply_read_unread_delete_filter_swipe(self):
        message_to_reply, reply_to_message_from_sender = 'something to reply to', 'this is a reply'
        self.home_1.jump_to_communities_home()
        self.home_1.get_chat(self.community_name, community=True).click()
        self.community_1.get_channel(self.channel_name).click()
        self.channel_1.send_message(message_to_reply)

        self.home_1.jump_to_communities_home()
        self.channel_2.chat_element_by_text(message_to_reply).wait_for_visibility_of_element(60)
        self.channel_2.quote_message(message_to_reply)
        self.channel_2.send_message(reply_to_message_from_sender)

        self.home_1.just_fyi("Checking unread indicators")
        self.home_1.notifications_unread_badge.wait_for_visibility_of_element(120)
        community_element_1 = self.home_1.get_chat(self.community_name, community=True)
        for unread_counter in community_element_1.new_messages_counter, self.home_1.communities_tab.counter:
            if not unread_counter.is_element_displayed(60):
                self.errors.append('New message counter badge is not shown!')
            if int(unread_counter.text) != 1:
                self.errors.append('New message counter badge is not 1, it is %s!' % unread_counter.text)

        self.home_1.just_fyi("Checking reply attributes in activity center")
        self.home_1.open_activity_center_button.click()
        reply_element = self.home_1.get_element_from_activity_center_view(reply_to_message_from_sender)
        if reply_element.title.text != 'Reply':
            self.errors.append("Expected title is not shown, '%s' is instead!" % reply_element.title)
        if not reply_element.unread_indicator.is_element_displayed():
            self.errors.append("No unread dot is shown on activity center element!")

        self.home_1.just_fyi("Swiping to 'Replies' on activity center and check unread there")
        self.home_1.mention_activity_tab_button.click()
        if reply_element.is_element_displayed(2):
            self.errors.append("Filter on mentions is not working in Activity centre!")
        self.home_1.reply_activity_tab_button.click()
        if not self.home_1.reply_activity_tab_button.counter.is_element_displayed(2):
            self.errors.append("No unread dot is shown on activity center tab element!")
        if not reply_element.is_element_displayed():
            self.errors.append("Filter on replies tab is not working in Activity centre!")

        self.home_1.just_fyi("Mark it as read and check filter")
        reply_element.swipe_right_on_element()
        self.home_1.activity_notification_swipe_button.click()
        if reply_element.is_element_displayed(2):
            self.errors.append("Message is not marked as read!")
        self.home_1.activity_unread_filter_button.click()
        if not reply_element.is_element_displayed(2):
            self.errors.append("Read filter is not displayed read message!")

        self.home_1.just_fyi("Mark it as unread and check filter via right swipe")
        reply_element.swipe_right_on_element()
        self.home_1.activity_notification_swipe_button.click()
        if not reply_element.unread_indicator.is_element_displayed():
            self.errors.append("No unread dot is shown on activity center element after marking it as unread!")

        self.home_1.just_fyi("Tap on it and check it marked as read")
        reply_element.click()
        if not self.channel_1.chat_element_by_text(reply_to_message_from_sender).is_element_displayed():
            self.errors.append("Was not redirected to chat after tapping on reply!")
        self.home_1.jump_to_communities_home()
        if self.home_1.notifications_unread_badge.is_element_displayed():
            self.errors.append("Notification was not marked as read after opening it in community channel!")

        self.home_1.just_fyi("Delete it from unread via left swipe")
        self.home_1.open_activity_center_button.click()
        reply_element.swipe_left_on_element()
        self.home_1.activity_notification_swipe_button.click()
        if reply_element.is_element_displayed():
            self.errors.append("Reply is still shown after removing from activity centre!")

        self.home_1.just_fyi("Reset filter to show all AC notifications again")
        self.home_1.reply_activity_tab_button.click()
        self.home_1.mention_activity_tab_button.click()
        self.home_1.all_activity_tab_button.click()
        self.home_1.close_activity_centre.click()

        self.errors.verify_no_errors()

    @marks.testrail_id(702957)
    def test_activity_center_mentions(self):
        if not self.channel_2.chat_message_input.is_element_displayed():
            self.home_2.click_system_back_button_until_element_is_shown()
            self.home_2.communities_tab.click()
            self.home_2.get_chat(self.community_name, community=True).click()
            self.community_2.get_channel(self.channel_name).click()
        self.home_1.jump_to_communities_home()

        self.device_2.just_fyi("Invited member sends a message with a mention")
        self.channel_2.mention_user(self.username_1)
        self.channel_2.send_message_button.click()

        self.home_1.just_fyi("Checking unread indicators")
        self.home_1.notifications_unread_badge.wait_for_visibility_of_element(120)
        community_element_1 = self.home_1.get_chat(self.community_name, community=True)
        for unread_counter in community_element_1.new_messages_counter, self.home_1.communities_tab.counter:
            if not unread_counter.is_element_displayed(60):
                self.errors.append('New message counter badge is not shown while mentioned!')
            if int(unread_counter.text) != 1:
                self.errors.append('New message counter badge is not 1, it is %s!' % unread_counter.text)

        self.home_1.just_fyi("Checking mention attributes in activity center")
        self.home_1.open_activity_center_button.click()
        mention_element = self.home_1.get_element_from_activity_center_view('@%s' % self.username_1)
        if mention_element.title.text != 'Mention':
            self.errors.append("Expected title is not shown, '%s' is instead!" % mention_element.title)
        if not mention_element.unread_indicator.is_element_displayed():
            self.errors.append("No unread dot is shown on activity center element (mention)!")
        if mention_element.message_body.text != '@%s' % self.username_1:
            self.errors.append("Mention body in activity center does not match expected, it is %s!" % mention_element.message_body.text)

        self.home_1.just_fyi("Tap on it and check redirect to channel")
        mention_element.click()
        if not self.channel_1.chat_element_by_text(self.username_1).is_element_displayed():
            self.errors.append("Was not redirected to chat after tapping on mention!")
        self.errors.verify_no_errors()

    @marks.testrail_id(702958)
    def test_activity_center_admin_notification_accept_swipe(self):
        self.home_2.just_fyi("Clearing history")
        self.home_2.click_system_back_button_until_element_is_shown()
        self.home_2.chats_tab.click()
        self.home_2.clear_chat_long_press(self.username_1)

        [home.jump_to_communities_home() for home in (self.home_1, self.home_2)]
        self.home_1.just_fyi("Open community to message")
        self.home_1.communities_tab.click()
        community_name = 'commun_to_check_notif'
        self.channel_name = self.home_1.get_random_chat_name()
        self.home_1.create_community(name=community_name, description='community to test', require_approval=True)
        self.home_1.reopen_app()
        community_element = self.home_1.get_chat(community_name, community=True)
        self.community_1.share_community(community_element, self.username_2)

        self.home_2.just_fyi("Request access to community")
        self.home_2.jump_to_messages_home()
        self.chat_2 = self.home_2.get_chat(self.username_1).click()
        self.chat_2.element_by_text_part('View').click()
        self.community_2.join_community()
        [home.jump_to_communities_home() for home in (self.home_1, self.home_2)]

        self.home_1.just_fyi("Checking unread indicators")
        self.home_1.notifications_unread_badge.wait_for_visibility_of_element(120)
        self.home_1.open_activity_center_button.click()
        reply_element = self.home_1.get_element_from_activity_center_view(self.username_2)
        if reply_element.title.text != 'Join request':
            self.errors.append("Expected title is not shown, '%s' is instead!" % reply_element.title)
        if not reply_element.unread_indicator.is_element_displayed():
            self.errors.append("No unread dot is shown on activity center element!")
        reply_element.swipe_right_on_element()
        self.home_1.activity_notification_swipe_button.click()
        self.home_1.close_activity_centre.click()

        self.home_2.just_fyi("Checking that community appeared on thr list")
        if not self.home_2.element_by_text_part(community_name).is_element_displayed(30):
            self.errors.append("Community is not appeared in the list after accepting admin request from activity centre")
        self.errors.verify_no_errors()
