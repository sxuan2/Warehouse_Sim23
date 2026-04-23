(function() {
    'use strict';
    document.addEventListener('DOMContentLoaded', function() {
        const countrySelect = document.querySelector('#id_country');
        let stateField = document.querySelector('#id_state');
        let tzField = document.querySelector('#id_time_zone');

        if (!countrySelect) return;

        async function updateFields() {
            const countryId = countrySelect.value;
            if (!countryId) return;

            try {
                // 确保路径符合你的总路由和子路由拼接
                const response = await fetch(`/api/warehouses/api/regions/?country=${countryId}`);
                const data = await response.json();

                // 联动州
                if (stateField) {
                    const currentVal = stateField.value;
                    const select = document.createElement('select');
                    select.name = 'state'; select.id = 'id_state'; select.style.width = '264px';
                    select.innerHTML = '<option value="">---------</option>';
                    data.regions.forEach(item => {
                        const opt = new Option(item.n, item.v);
                        if (item.v === currentVal) opt.selected = true;
                        select.appendChild(opt);
                    });
                    stateField.replaceWith(select);
                    stateField = select;
                }

                // 联动时区
                if (tzField) {
                    const currentTz = tzField.value;
                    const select = document.createElement('select');
                    select.name = 'time_zone'; select.id = 'id_time_zone'; select.style.width = '264px';
                    select.innerHTML = '<option value="">---------</option>';
                    data.timezones.forEach(item => {
                        const opt = new Option(item.n, item.v);
                        if (item.v === currentTz) opt.selected = true;
                        select.appendChild(opt);
                    });
                    tzField.replaceWith(select);
                    tzField = select;
                }
            } catch (e) { console.error(e); }
        }

        countrySelect.addEventListener('change', updateFields);
        if (countrySelect.value) updateFields();
    });
})();