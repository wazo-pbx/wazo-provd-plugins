<?xml version="1.0" encoding="UTF-8"?>
<settings>
  <phone-settings e="2">
    <locale perm="RW">{{ XX_locale|e }}</locale>
    <alert_external_ring_sound perm="$">Ringer2</alert_external_ring_sound>
    <alert_external_ring_text perm="$">external</alert_external_ring_text>
    <alert_group_ring_sound perm="$">Ringer3</alert_group_ring_sound>
    <alert_group_ring_text perm="$">queue</alert_group_ring_text>
    <internal_ringer_file idx="0" perm="">Ringer4</internal_ringer_file>
    <internal_ringer_text idx="0" perm="">ivr</internal_ringer_text>
    <auto_reboot_on_setting_change perm="">on</auto_reboot_on_setting_change>
    <cache_contact_details idx="1" perm="">off</cache_contact_details>
    <call_screen_fkeys_on_connected perm="">F_LEFT F_RIGHT F_CONF_ON F_HOLD transfer(not:Transfer) F_DUAL_AUDIO(not:Conference) F_DELETE_MSG F_CALLRECORD_CONTROL_ON</call_screen_fkeys_on_connected>
    <call_screen_fkeys_on_holding perm="">F_LEFT F_RIGHT F_CONF_ON(not:Transfer) F_DIAL(Transfer) F_HOLD transfer(not:Transfer) F_CONTACTPOOL(Holding,Transfer) F_ABS F_DELETE_MSG F_CALLRECORD_CONTROL_ON </call_screen_fkeys_on_holding>
    <cancel_on_hold perm="">on</cancel_on_hold>
    <status_msgs_that_are_blocked perm="">EmergencyCallNumbersMisconfigured PhoneHasVoiceMessages PhoneHasTextMessages PhoneProvisioningFailed CurrentIdentityIsDnd RingerIsSilent AnonymousIdOn AudioDeviceIsviceIsSpeaker AudioDeviceIsHeadset AudioDeviceIsHandset</status_msgs_that_are_blocked>
    <status_msgs_that_show_directly perm="">StatusLineSystemMessage:3 AudioDeviceIsSpeaker AudioDeviceIsHeadset AudioIsMuted CallBackOnBusyInProgress CallBackOnBusyAvailable PhoneProvisioningStarting PhoneProvisioningInProgress PhoneHasIncomingPublicAnnouncement PhoneIsLocked EthernetUnplugged PhoneHasFirmwareUpdate FirmwareUpdateFailed PhoneWantsToUpdate VisionConnectionLost PhoneWantsReboot PhoneHasDisabledSipStack PhoneHasVpnError PhoneHasLowMemory PhoneRefusedHugeXcapSync CurrentIdentityIsNotRegistered PhoneIsWaitingForCallCompletion CurrentIdentityForewardsAlways CurrentIdentityIsDnd CurrentIdentityForewardsWhenBusy CurrentIdentityForewardsAfterTimeout PhoneWaitsOnNtpServer PhoneCannotReachNtpServer ActiveLocations PhoneHasNoHttpPassword PhoneHasNoAdminPassword ServerMessageToBeShownDirectly CurrentIdentityHasVoiceMessages PhoneHasMissedCalls CurrentIdentityHasTextMessages TryParking:5 UxmConnected:5 WlanActive:5 HidConnecting:10 HidConnected:5 ExpDeviceCabelingBroken ExpDeviceLimitExceeded CanceledCall:3</status_msgs_that_show_directly>
    <transfer_on_hangup perm="">on</transfer_on_hangup>
    <transfer_on_hangup_non_pots perm="">on</transfer_on_hangup_non_pots>
    <transfer_on_hangup_with_starcode perm="">on</transfer_on_hangup_with_starcode>

    {% if vlan_enabled -%}
    <vlan_id perm="R">{{ vlan_id }}</vlan_id>
    <vlan_qos perm="R">{{ vlan_priority|d('0') }}</vlan_qos>
    {% else -%}
    <vlan_id perm="R"></vlan_id>
    <vlan_qos perm="R"></vlan_qos>
    {% endif -%}

    <codec_tos perm="R">184</codec_tos>
    <signaling_tos perm="R">184</signaling_tos>

    <setting_server perm="RW">{{ XX_server_url }}</setting_server>

    {% if user_username -%}
    <webserver_user_name perm="R">{{ user_username|e }}</webserver_user_name>
    {% endif -%}
    {% if user_password -%}
    <webserver_user_password perm="R">{{ user_password|e }}</webserver_user_password>
    {% endif -%}

    {% if admin_username -%}
    <http_user perm="R">{{ admin_username|e }}</http_user>
    <webserver_admin_name perm="R">{{ admin_username|e }}</webserver_admin_name>
    {% endif -%}
    {% if admin_password -%}
    <http_pass perm="R">{{ admin_password|e }}</http_pass>
    <admin_mode_password perm="R">{{ admin_password|e }}</admin_mode_password>
    <webserver_admin_password perm="R">{{ admin_password|e }}</webserver_admin_password>
    {% endif -%}

    {% if ntp_enabled -%}
    <ntp_server perm="R">{{ ntp_ip }}</ntp_server>
    {% else -%}
    <ntp_server perm="R"></ntp_server>
    {% endif -%}

    {% for line_no, line in sip_lines.items() %}
    <user_active idx="{{ line_no }}" perm="R">on</user_active>
    <user_idle_text idx="{{ line_no }}" perm="R">{{ line['display_name']|e }}</user_idle_text>
    <user_idle_number idx="{{ line_no }}" perm="R">{{ line['number'] }}</user_idle_number>
    <user_host idx="{{ line_no }}" perm="R">{{ line['proxy_ip'] }}</user_host>
    <user_outbound idx="{{ line_no }}" perm="R">{{ line['proxy_ip'] }}:{{ line['proxy_port']
      }};transport={{ XX_sip_transport }}</user_outbound>
    {% if XX_sip_transport == 'tls' and line['number'] != 'autoprov' -%}
    <user_srtp idx="{{ line_no }}" perm="R">on</user_srtp>
    {% else -%}
    <user_srtp idx="{{ line_no }}" perm="R">off</user_srtp>
    {% endif %}
    <user_savp idx="{{ line_no }}" perm="R">mandatory</user_savp>
    <user_auth_tag idx="{{ line_no }}" perm="R">off</user_auth_tag>
    <user_name idx="{{ line_no }}" perm="R">{{ line['username']|e }}</user_name>
    <user_pname idx="{{ line_no }}" perm="R">{{ line['auth_username']|e }}</user_pname>
    <user_pass idx="{{ line_no }}" perm="R">{{ line['password']|e }}</user_pass>
    <user_realname idx="{{ line_no }}" perm="R">{{ line['display_name']|e }}</user_realname>
    <user_mailbox idx="{{ line_no }}" perm="R">{{ line['voicemail'] }}</user_mailbox>
    <user_dtmf_info idx="{{ line_no }}" perm="R">{{ line['XX_user_dtmf_info'] }}</user_dtmf_info>
    <codec_priority_list idx="{{ line_no }}" perm="R">pcma,pcmu,g722,g729,telephone-event</codec_priority_list>
    {% if line['backup_proxy_ip'] -%}
    <user_failover_identity idx="{{ line_no }}" perm="R">{{ line_no|int + 1 }}</user_failover_identity>

    <user_active idx="{{ line_no|int + 1 }}" perm="R">on</user_active>
    <user_idle_text idx="{{ line_no|int + 1 }}" perm="R">{{ line['display_name']|e }} {{
      line['number'] }}</user_idle_text>
    <user_host idx="{{ line_no|int + 1 }}" perm="R">{{ line['backup_proxy_ip'] }}</user_host>
    <user_outbound idx="{{ line_no|int + 1 }}" perm="R">{{ line['proxy_ip'] }}:{{ line['proxy_port']
      }};transport={{ XX_sip_transport }}</user_outbound>
    {% if XX_sip_transport == 'tls' and line['number'] != 'autoprov' -%}
    <user_srtp idx="{{ line_no|int + 1 }}" perm="R">on</user_srtp>
    {% else -%}
    <user_srtp idx="{{ line_no|int + 1 }}" perm="R">off</user_srtp>
    {% endif %}
    <user_savp idx="{{ line_no|int + 1 }}" perm="R">mandatory</user_savp>
    <user_auth_tag idx="{{ line_no|int + 1 }}" perm="R">off</user_auth_tag>
    <user_name idx="{{ line_no|int + 1 }}" perm="R">{{ line['username']|e }}</user_name>
    <user_pname idx="{{ line_no|int + 1 }}" perm="R">{{ line['auth_username']|e }}</user_pname>
    <user_pass idx="{{ line_no|int + 1 }}" perm="R">{{ line['password']|e }}</user_pass>
    <user_realname idx="{{ line_no|int + 1 }}" perm="R">{{ line['display_name']|e }}</user_realname>
    <user_mailbox idx="{{ line_no|int + 1 }}" perm="R">{{ line['voicemail'] }}</user_mailbox>
    <user_dtmf_info idx="{{ line_no|int + 1 }}" perm="R">{{ line['XX_user_dtmf_info'] }}</user_dtmf_info>
    <hide_identity idx="{{ line_no|int + 1 }}" perm="R">true</hide_identity>
    {% endif -%}

    {% endfor -%}
    <context_key_label idx="0" perm="RW">Menu</context_key_label>
    {% if XX_xivo_phonebook_url -%}
    <context_key idx="3" perm="RW">
      <action>
        <url when="on press" target="{{ XX_xivo_phonebook_url|e }}" />
      </action>
    </context_key>
    <context_key_icon_type idx="3" perm="RW">kIconTypeFkeyAdrBook</context_key_icon_type>
    <context_key_label idx="3" perm="RW">{{ XX_dict['remote_directory'] }}</context_key_label>
    {% block gui_fkey %}
    {% endblock %}
    {% endif -%}
    <context_key idx="2" perm="RW">redirect </context_key>


    {% if XX_lang -%}
    <language perm="R">{{ XX_lang[0] }}</language>
    <web_language perm="R">{{ XX_lang[0] }}</web_language>
    <tone_scheme perm="R">{{ XX_lang[1] }}</tone_scheme>
    {% endif -%}

    {{ XX_timezone }}

    <!-- hide the "identity not registered" msg when Wazo HA is enabled -->
    <status_msgs_that_are_blocked perm="R">EmergencyCallNumbersMisconfigured PhoneHasVoiceMessages PhoneHasTextMessages PhoneProvisioningFailed CurrentIdentityIsDnd RingerIsSilent AnonymousIdOn AudioDeviceIsviceIsSpeaker AudioDeviceIsHeadset AudioDeviceIsHandset PhoneHasVoiceMessages PhoneHasTextMessages{{XX_msgs_blocked }}</status_msgs_that_are_blocked>

    <call_waiting perm="R">{{ 'off' if XX_options['switchboard'] else 'on' }}</call_waiting>
    <quick_transfer perm="R">attended</quick_transfer>
    <mute_is_dnd_in_idle perm="R">on</mute_is_dnd_in_idle>
    {% block settings_suffix %}
    {% endblock %}
  </phone-settings>
  <functionKeys>
    {% block fkeys_prefix %}{% endblock %}
    {{ XX_fkeys }}
  </functionKeys>
</settings>
