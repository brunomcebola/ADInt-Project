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
  `;

  for (var option of options) {
    checkbox = `
      <div class="ui checkbox">
        <input type="radio" name="sub_type_id" value=${option.id}>
        <label style="margin-right: 20px; padding-left: 20px">${option.name}</label>
      </div>
    `;

    form += checkbox;
  }

  form += `
      </div>

      <div class="field">
        <h3>Description</h3>
        <textarea name="description"></textarea>
      </div>

      <button class="ui button primary" type="submit">Save activity</button>
    </form>
  `;

  return form;
}
