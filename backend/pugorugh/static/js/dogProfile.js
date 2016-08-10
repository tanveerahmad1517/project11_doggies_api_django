var DogProfile = React.createClass({

  displayName: 'DogProfile',

  mixins: [React.addons.LinkedStateMixin],

  getInitialState: function () {
    return { name: '', age: '', breed: '', gender: 'u', image: '' };
  },

  getDog: function () {
    this.serverRequest = $.ajax({
      url: `api/dog/${ this.state.details ? this.state.details.id : -1 }/${ this.state.filter }/next/`,
      method: "GET",
      dataType: "json",
      headers: TokenAuth.getAuthHeader()
    }).done(function (data) {
      this.setState({ details: data, message: undefined });
    }.bind(this)).fail(function (response) {
      var message = null;
      if (response.status == 404) {
        if (this.state.filter == "undecided") {
          message = "No dogs matched your preferences.";
        } else {
          message = `You don't have any ${ this.state.filter } dogs.`;
        }
      } else {
        message = response.error;
      }
      this.setState({ message: message, details: undefined });
    }.bind(this));
  },  
    
  save: function () {
    var file_data = $("#dog-image").prop('files')[0];
    var form_data = new FormData();
    if(file_data) {form_data.append('image', file_data);};
    form_data.append('name', this.state.name);
    form_data.append('breed', this.state.breed);
    form_data.append('age', this.state.age);
    form_data.append('gender', this.state.gender);

    $.ajax({
      url: "api/dog/" + self.state.id,
      cache: false,
      type: "POST",
      contentType: false,
      processData: false,
      headers: TokenAuth.getAuthHeader(),
      data: form_data,
      success: this.props.setView.bind(this, 'undecided'),
      error: function (req, status) {
        console.log(status);
      }
    });
  },

  makeValueLink: function (e) {
    this.setState({gender: e.target.value});
  },

  disabled: function () {
    return this.state.name == '' || this.state.age == '';
  },

  render: function () {
    return React.createElement(
      'div',
      null,
      React.createElement(
        'p',
        { 'class': 'text-centered' },
        this.state.message
      ),
      React.createElement('label', null, 'Image'),
      React.createElement('input', { type: 'file', id: 'dog-image', valueLink: this.linkState('image') }),
      React.createElement('label', null, 'Name*'),
      React.createElement('input', { type: 'text', id: 'dog-name', valueLink: this.linkState('name') }),
      React.createElement('label', null, 'Breed'),
      React.createElement('input', { type: 'text', id: 'dog-breed', valueLink: this.linkState('breed') }),
      React.createElement('label', null, 'Age (months)*'),
      React.createElement('input', { type: 'text', id: 'dog-age', valueLink: this.linkState('age') }),
      React.createElement('label', null, 'Gender'),
      React.createElement('label', null,
        React.createElement('input', { type: 'radio', name: 'gender', value: 'm', onChange: this.makeValueLink }),
        React.createElement('span', { className: 'label-body' }, 'Male')
      ),
      React.createElement('label', null,
        React.createElement('input', { type: 'radio', name: 'gender', value: 'f', onChange: this.makeValueLink }),
        React.createElement('span', { className: 'label-body' }, 'Female')
      ),
      React.createElement('label', null,
        React.createElement('input', { type: 'radio', name: 'gender', value: 'u', defaultChecked: true, onChange: this.makeValueLink }),
        React.createElement('span', { className: 'label-body' }, 'Unknown')
      ),
      React.createElement('br'),
      React.createElement(
        'button',
        { onClick: this.save, disabled: this.disabled() },
        'Save'
      ),
      React.createElement(
        'p',
        { 'class': 'text-centered' },
        '*Required field'
      )
    );
  }
});