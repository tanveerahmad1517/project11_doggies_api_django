var AddDog = React.createClass({

  displayName: 'AddDog',

  mixins: [React.addons.LinkedStateMixin],

  getInitialState: function () {
    return { name: '', age: '', gender: 'u', image: '' };
  },

  save: function () {
    var json = JSON.stringify({
      name: this.state.name,
      breed: this.state.breed,
      age: this.state.age,
      gender: this.state.gender,
    });

    $.ajax({
      url: "api/dog/new/",
      method: "POST",
      dataType: "json",
      headers: $.extend({ 'Content-type': 'application/json' }, TokenAuth.getAuthHeader()),
      data: json,
      success: this.props.setView.bind(this, 'undecided')
    });

  },

  makeValueLink: function (e) {
    this.setState({gender: e.target.value});
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
      React.createElement('label', null, 'Name'),
      React.createElement('input', { type: 'text', id: 'dog-name', valueLink: this.linkState('name') }),
      React.createElement('label', null, 'Breed'),
      React.createElement('input', { type: 'text', id: 'dog-breed', valueLink: this.linkState('breed') }),
      React.createElement('label', null, 'Age (months)'),
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
        { onClick: this.save },
        'Save'
      )
    );
  }
});