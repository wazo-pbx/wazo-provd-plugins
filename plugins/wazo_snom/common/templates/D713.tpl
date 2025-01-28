{% extends 'base.tpl' -%}

    {% block gui_fkey %}
    {% if XX_xivo_phonebook_url -%}
    <context_key idx="0" perm="R">
      <initialization>
        <variable name="label" value="{{ XX_dict['remote_directory'] }}"/>
        <variable name="icon" value="kIconTypeFkeyAdrBook"/>
      </initialization>
      <action>
        <url target="{{ XX_xivo_phonebook_url|e }}" when="on press"/>
      </action>
    </context_key>
    {% else -%}
    <context_key idx="0" perm="R">keyevent F_ADR_BOOK</gui_fkey1>
    {% endif -%}
    <context_key idx="1" perm="R">keyevent F_REDIRECT</context_key>
    <context_key idx="2" perm="R">keyevent F_CALL_LIST</context_key>
    <context_key idx="3" perm="R">keyevent F_STATUS</context_key>
    {% endblock %}

    {% block settings_suffix %}{% endblock %}
