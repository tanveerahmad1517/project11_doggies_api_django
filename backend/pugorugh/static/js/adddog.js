var AddDog = React.createClass({

  displayName: 'AddDog',

  mixins: [React.addons.LinkedStateMixin],

  getInitialState: function () {
    return { name: '', date_of_birth: '', breed: '', gender: 'm', image: '', message: undefined, intact_or_neutered: 'i', size: 's' };
  },

  save: function () {
    var file_data = $("#dog-image").prop('files')[0];
    var form_data = new FormData();
    if(file_data) {form_data.append('image', file_data)}
    if($.trim(this.state.name)) {form_data.append('name', $.trim(this.state.name))}
    if($.trim(this.state.breed)) {form_data.append('breed', $.trim(this.state.breed))}
    if(this.state.date_of_birth) {form_data.append('date_of_birth', this.state.date_of_birth)}
    if(this.state.gender) {form_data.append('gender', this.state.gender)}
    if(this.state.intact_or_neutered) {form_data.append('intact_or_neutered', this.state.intact_or_neutered)}
    if(this.state.size) {form_data.append('size', this.state.size)}

    $.ajax({
      url: "api/dog/",
      cache: false,
      type: "POST",
      contentType: false,
      processData: false,
      headers: TokenAuth.getAuthHeader(),
      data: form_data,
      success: this.props.setView.bind(this, 'undecided'),
      error: function (response, status) {
        this.setState({ message: response.responseText});
      }.bind(this)
    });
  },

  makeValueLinkSize: function (e) {
    this.setState({size: e.target.value});
  },

  makeValueLinkGender: function (e) {
    console.log(e.target.name);
    this.setState({gender: e.target.value});
  },

  makeValueLinkIntactOrNeutered: function (e) {
    this.setState({intact_or_neutered: e.target.value});
  },

  disabled: function () {
    return $.trim(this.state.name) == '' || this.state.date_of_birth == '';
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
      React.createElement('label', null, 'Date of birth*'),
      React.createElement('input', { type: 'date', id: 'dog-age', valueLink: this.linkState('date_of_birth') }),
      React.createElement('label', null, 'Gender*'),
      React.createElement('label', null,
        React.createElement('input', { type: 'radio', name: 'gender', value: 'm', defaultChecked: true, onChange: this.makeValueLinkGender }),
        React.createElement('span', { className: 'label-body' }, 'Male')
      ),
      React.createElement('label', null,
        React.createElement('input', { type: 'radio', name: 'gender', value: 'f', onChange: this.makeValueLinkGender }),
        React.createElement('span', { className: 'label-body' }, 'Female')
      ),
      // React.createElement('label', null,
      //   React.createElement('input', { type: 'radio', name: 'gender', value: 'u', onChange: this.makeValueLinkGender }),
      //   React.createElement('span', { className: 'label-body' }, 'Unknown')
      // ),
      React.createElement('label', null, 'Intact or Neutered*'),
      React.createElement('label', null,
        React.createElement('input', { type: 'radio', name: 'intact_or_neutered', value: 'i', defaultChecked: true, onChange: this.makeValueLinkIntactOrNeutered }),
        React.createElement('span', { className: 'label-body' }, 'Intact')
      ),
      React.createElement('label', null,
        React.createElement('input', { type: 'radio', name: 'intact_or_neutered', value: 'n', onChange: this.makeValueLinkIntactOrNeutered }),
        React.createElement('span', { className: 'label-body' }, 'Neutered')
      ),
      React.createElement('label', null, 'Size*'),
      React.createElement('label', null,
        React.createElement('input', { type: 'radio', name: 'size', value: 's', defaultChecked: true, onChange: this.makeValueLinkSize }),
        React.createElement('span', { className: 'label-body' }, 'Small')
      ),
      React.createElement('label', null,
        React.createElement('input', { type: 'radio', name: 'size', value: 'm', onChange: this.makeValueLinkSize }),
        React.createElement('span', { className: 'label-body' }, 'Medium')
      ),  
      React.createElement('label', null,
        React.createElement('input', { type: 'radio', name: 'size', value: 'l', onChange: this.makeValueLinkSize }),
        React.createElement('span', { className: 'label-body' }, 'Large')
      ),
      React.createElement('label', null,
        React.createElement('input', { type: 'radio', name: 'size', value: 'xl', onChange: this.makeValueLinkSize }),
        React.createElement('span', { className: 'label-body' }, 'Extra Large')
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