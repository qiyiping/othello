import React, { Component } from 'react';
// import logo from './logo.svg';
// import './App.css';

class Board extends Component {
  constructor() {
    super();
    this.state = {"board":[[0,0,0,0,0,0,0,0],
                           [0,0,0,0,0,0,0,0],
                           [0,0,0,0,0,0,0,0],
                           [0,0,0,2,1,0,0,0],
                           [0,0,0,1,2,0,0,0],
                           [0,0,0,0,0,0,0,0],
                           [0,0,0,0,0,0,0,0],
                           [0,0,0,0,0,0,0,0]],
                  "options":[[2,3],[3,2],[4,5],[5,4]],
                  "blackScore": 2,
                  "whiteScore": 2,
                  "gameStarted": false,
                  "humanPlayer": "black",
                  "aiPlayer": "white",
                  "turn":"black"};

    this.boardSize = 320;
    this.gridSize = this.boardSize/8;

    this.newGame = this.newGame.bind(this);
    this.handleClick = this.handleClick.bind(this);
    this.changePlayer = this.changePlayer.bind(this);
  }

  changePlayer(e) {
    this.setState({
      "humanPlayer": e.target.value,
      "aiPlayer": this.opponent(e.target.value),
      "turn": e.target.value
    });
  }

  opponent(player) {
    if (player === "black") {
      return "white";
    } else {
      return "black";
    }
  }

  newGame() {
    fetch("/othello/new").then(response => {
      return response.json();
    }).then(js => {
      js["gameStarted"] = true;
      this.setState(js);
    });
  }

  componentDidMount() {
    this.updateCanvas();
  }

  componentDidUpdate() {
    this.updateCanvas();
    this.ai();
  }

  updateCanvas() {
    const ctx = this.refs.board.getContext('2d');
    this.drawBoard(ctx);
    this.drawPieces(ctx);
    this.drawOptions(ctx);
  }

  drawSinglePiece(ctx, r, c, piece) {
    var alpha, style = [1.0, "black"];
    if (piece === 0) {
      alpha = 0.2;
    }
    if (piece === 2) {
      style = "white";
    }
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.arc((c+0.5) * this.gridSize, (r+0.5) * this.gridSize, this.gridSize/2-3, 0, Math.PI * 2, false);
    ctx.closePath();
    ctx.fillStyle = style;
    ctx.strokeStyle = style;
    ctx.fill();
    ctx.restore();
  }

  drawOptions(ctx) {
    for(var i = 0; i < this.state.options.length; i++) {
      var p = this.state.options[i];
      this.drawSinglePiece(ctx, p[0], p[1], 0);
    }
  }

  drawPieces(ctx) {
    for(var i = 0; i < 8; i++) {
      for(var j = 0; j < 8; j++) {
        var piece = this.state.board[i][j];
        if (piece !== 0) {
          this.drawSinglePiece(ctx, i, j, piece);
        }
      }
    }
  }

  drawBoard(ctx) {
    ctx.save();
    ctx.clearRect(0, 0, this.boardSize, this.boardSize);
    ctx.fillStyle = 'green';
    ctx.fillRect(0, 0, this.boardSize, this.boardSize);

    ctx.lineWidth = 1;
    ctx.strokeStyle="#111";
    ctx.fillStye="#111";
    ctx.beginPath();
    for(var i = 0; i <= 8; i++) {
      ctx.moveTo(0, this.gridSize * i);
      ctx.lineTo(this.boardSize, this.gridSize * i);
      ctx.moveTo(this.gridSize * i, 0);
      ctx.lineTo(this.gridSize * i, this.boardSize);
    }
    ctx.closePath();
    ctx.stroke();
    ctx.restore();
  }

  ai() {
    if (this.state.turn === this.state.aiPlayer) {
      this.play({});
    }
  }

  getClickPosition(e) {
    var rect = this.refs.board.getBoundingClientRect();
    var c = parseInt((e.clientX-rect.left) / this.gridSize);
    var r = parseInt((e.clientY-rect.top) / this.gridSize);
    return {row: r, col: c};
  }

  handleClick(e) {
    var pos = this.getClickPosition(e);
    var c = pos.col;
    var r = pos.row;
    var validClick = false;
    for(var i = 0; i < this.state.options.length; i++) {
      var p = this.state.options[i];
      if (r === p[0] && c === p[1]) {
        validClick = true;
        break;
      }
    }

    // console.log("click position:", r, c,
    //             " valid positon:", validClick,
    //             " turn:", this.state.turn,
    //             " human player:", this.state.humanPlayer);

    if (validClick && this.state.turn === this.state.humanPlayer) {
      this.play({"action": [r, c]});
    }
  }

  play(props) {
    // console.log(props, this.state.gameStarted);
    if (this.state.gameStarted) {
      var formData = new FormData();
      if ("action" in props) {
        formData.append("data", JSON.stringify({
          player: this.state.turn,
          action: props["action"],
          board: this.state.board
        }));
      } else {
        formData.append("data", JSON.stringify({
          player: this.state.turn,
          board: this.state.board
        }));
      }

      fetch("/othello/play", {
        method: "post",
        body: formData
      }).then(response => {
        return response.json();
      }).then(js => {
        this.setState(js);
      });
    }
  }

  render() {
    return (
      <div>
        <select onChange={this.changePlayer}>
          <option value="black">Black</option>
          <option value="white">White</option>
        </select>
        <button onClick={this.newGame}>Start Game</button>
        <br/>
        Black Score: {this.state.blackScore}, White Score: {this.state.whiteScore}
        <br/>
        <canvas ref="board" width={this.boardSize} height={this.boardSize} onClick={this.handleClick}></canvas>
      </div>
    );
  }
}

class App extends Component {
  render() {
    return (
      <div className="app">
        <Board />
      </div>
    );
  }
}

export default App;
