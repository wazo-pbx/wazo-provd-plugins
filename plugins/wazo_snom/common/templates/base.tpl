<?xml version="1.0" encoding="UTF-8" ?>
<settings>
  <phone-settings>
    {% if vlan_enabled -%}
    <vlan_id perm="R">{{ vlan_id }}</vlan_id>
    <vlan_qos perm="R">{{ vlan_priority|d('0') }}</vlan_qos>
    <vlan_pc_id perm="R">{{ vlan_pc_port_id|d('0') }}</vlan_pc_id>
    {% endif -%}

    <codec_tos perm="R">184</codec_tos>
    <signaling_tos perm="R">184</signaling_tos>

    <setting_server perm="RW">{{ XX_server_url }}/</setting_server>

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
    {% endif -%}

    {% for line_no, line in sip_lines.items() %}
    <user_active idx="{{ line_no }}" perm="R">on</user_active>
    <user_idle_text idx="{{ line_no }}" perm="R">{{ line['display_name']|e }}</user_idle_text>
    <user_idle_number idx="{{ line_no }}" perm="R">{{ line['number'] }}</user_idle_number>
    <user_host idx="{{ line_no }}" perm="R">{{ line['proxy_ip'] }}</user_host>
    <user_outbound idx="{{ line_no }}" perm="R">{{ line['proxy_ip'] }}:{{ line['proxy_port'] }};transport={{ XX_sip_transport }}</user_outbound>
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
    <user_idle_text idx="{{ line_no|int + 1 }}" perm="R">{{ line['display_name']|e }} {{ line['number'] }}</user_idle_text>
    <user_host idx="{{ line_no|int + 1 }}" perm="R">{{ line['backup_proxy_ip'] }}</user_host>
    <user_outbound idx="{{ line_no|int + 1 }}" perm="R">{{ line['proxy_ip'] }}:{{ line['proxy_port'] }};transport={{ XX_sip_transport }}</user_outbound>
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

    {% if XX_xivo_phonebook_url -%}
    <dkey_directory perm="R">url {{ XX_xivo_phonebook_url|e }}</dkey_directory>
    {% endif -%}

    {% block gui_fkey %}{% endblock %}

    {% if XX_lang -%}
    <language perm="R">{{ XX_lang[0] }}</language>
    <web_language perm="R">{{ XX_lang[0] }}</web_language>
    <tone_scheme perm="R">{{ XX_lang[1] }}</tone_scheme>
    {% endif -%}

    {{ XX_timezone }}

    <!-- hide the "identity not registered" msg when Wazo HA is enabled -->
    <status_msgs_that_are_blocked perm="R">{{ XX_msgs_blocked }}</status_msgs_that_are_blocked>

    <call_waiting perm="R">{{ 'off' if XX_options['switchboard'] else 'on' }}</call_waiting>

    {% block settings_suffix %}{% endblock %}
  </phone-settings>
  <functionKeys>
    {% block fkeys_prefix %}{% endblock %}
    {{ XX_fkeys }}
  </functionKeys>
</settings>
