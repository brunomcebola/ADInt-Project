function createSuccessMessage(id, name) {
  successMessage = `
    <div class="ui message success hidden" id="success_${id}">
      <div class="header">Successful submition</div>
      <p>${name} activity saved with success!</p>
      <div class="line-fade"></div>
    </div>
  `;

  return successMessage;
}

function createErrorMessage(id, name) {
  errorMessage = `
    <div class="ui message negative hidden" id="error_${id}">
      <div class="header">Submition failure</div>
      <p>Error saving ${name} activity!</p>
      <div class="line-fade"></div>
    </div>
  `;

  return errorMessage;
}

function createForm(id, options) {
  var form = `
    <form class="ui form" id="form_${id}" type_id=${id}>
      <div class="field">
        <div class="two fields">
          <div class="field ui calendar" id="start_time">
            <h3>Start Time <span class="required">*</span></h3>
            <div class="ui input left icon">
              <i class="calendar icon"></i>
              <input type="text" name="start_time" placeholder="Start time" />
            </div>
          </div>

          <div class="field ui calendar" id="stop_time">
            <h3>Stop Time <span class="required">*</span></h3>
            <div class="ui input left icon">
              <i class="calendar icon"></i>
              <input type="text" name="stop_time" placeholder="Stop time" />
            </div>
          </div>
        </div>
      </div>

      <div class="field">
        <h3>Activity type <span class="required">*</span></h3>
        <div>
  `;

  for (let option of options) {
    form += `
          <div style="display: inline-block">
            <div class="ui radio checkbox">
              <input type="radio" name="sub_type_id" value=${option.id}>
              <label style="margin-right: 20px; padding-left: 20px">${option.name}</label>
            </div>
          </div>
    `;
  }

  form += `
        </div>
        <div class="two fields">
          <div class="field" id="options">
          </div>
        </div>
      </div>
  `;

  form += `
      <div class="field">
        <h3>Description</h3>
        <textarea name="description"></textarea>
      </div>

      <button class="ui button primary" type="submit">Save activity</button>
    </form>
  `;

  return form;
}

function createOptions() {
  return `
    <div class="ui selection dropdown" style="margin-top: 20px">
      <input name="external_id" type="hidden">
      <div class="default text">Select a value</div>
      <i class="dropdown icon"></i>
      <div class="menu">
          <div class="item" data-value="1">Value</div>
          <div class="item" data-value="2">Another Value</div>
      </div>
    </div>
  `;
}

function generateTable(items, page, perPage) {
  var table = `
    <table class="ui celled padded table">
      <thead>
        <tr>
          <th class="single line">Activity</th>
          <th class="single line">Type</th>
          <th class="single line">Start Time</th>
          <th class="single line">Finish Time</th>
          <th class="single line">Duration</th>
          <th class="single line">Description</th>
        </tr>
      </thead>
      <tbody>
  `;

  for (let item of items.slice(page * perPage, (page + 1) * perPage)) {
    let duration = item.stop_time - item.start_time;

    table += `
        <tr>
          <td class="single line">${item.type_name}</td>
          <td class="single line">${item.sub_type_name}</td>
          <td class="single line">${item.start_time}</td>
          <td class="single line">${item.stop_time}</td>
          <td class="single line">${duration}</td>
          <td>${item.description}</td>
        </tr>
    `;
  }

  table += `
      </tbody>
      <tfoot>
        <tr>
          <th colspan="6">
            <div class="ui right floated pagination menu">
              <a class="icon item">
                <i class="left chevron icon"></i>
              </a>
  `;

  for (let i = 1; i <= Math.ceil(items.length / perPage); i++) {
    table += `
              <a class="item ${i == page + 1 ? "active" : ""}">${i}</a>
    `;
  }

  table += `
              <a class="icon item">
                <i class="right chevron icon"></i>
              </a>
            </div>
          </th>
        </tr>
      </tfoot>
    </table>
  `;

  return table;
}
