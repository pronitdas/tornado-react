import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import io from 'socket.io-client';

var socket = new WebSocket('ws://localhost:1234/socket');
const subredditTopic = ['futurology', 'explainlikeimfive', 'Nonononoyes' ,'NatureIsFuckingLit','announcements','funny','AskReddit','todayilearned','worldnews']


class App extends Component {

  constructor(props){
    super(props)
    this.state = {
      topics:{},
      currentFetch: ""
    }
    this.getData = this.getData.bind(this)
  }

  componentDidMount(){
    console.log(socket)
    socket.onmessage= this.getData;
  }

  getData(ev){
    const {topics} = this.state
    console.log(JSON.parse(ev.data))
    let {topic, posts} = JSON.parse(ev.data)
    
    topics[topic] = posts
    this.setState({topics, currentFetch:topic})
  }


  getPosts(topics, topic){
    let posts = topics[topic]
    return posts || []
  }

  render() {
    const {topics, currentFetch} = this.state;
    let posts = this.getPosts(topics, currentFetch)
    console.log(posts,'here', currentFetch, topics)
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />          
          <input  id="reddit"/>
          <button onClick={
            ()=>{
              var topic = document.getElementById('reddit').value              
              socket.send(JSON.stringify({category:topic}))
            }
          }>
            Get Subreddit
          </button>
        </header>        
        <section>
        <ul className="list-group list-group-horizontal">
          {subredditTopic.map((el)=>{
          return <li className="list-group-item"> 
          <button className="btn btn-primary" type="button" onClick={()=> {
           
            socket.send(JSON.stringify({category: el}))
          }}>
              {el}
            </button> 
          </li>
          })}         
        </ul>
     
      <div className="card card-body">
          
        <ul  className="list-group">
          {posts && posts.map((post)=>{
            return <li className="list-group-item">
              <h3>{post.title}</h3>
            </li>
          })}
        </ul>
       </div>
        </section>
      </div>
    );
  }
}

export default App;
