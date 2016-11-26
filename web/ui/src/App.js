import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

function guid() {
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
  }
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
}

String.prototype.format = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

function PlayRecordRow(props) {
  return (
    <div>
      {props.player} : {props.action[0] + 1}, {props.action[1] + 1}
    </div>
  );
}

class Board extends Component {
  constructor() {
    super();
    this.state = {
      board: [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 2, 1, 0, 0, 0],
        [0, 0, 0, 1, 2, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
      ],
      steps: [],
      options: [
        [2, 3],
        [3, 2],
        [4, 5],
        [5, 4]
      ],
      blackScore: 2,
      whiteScore: 2,
      gameStarted: false,
      humanPlayer: "black",
      aiPlayer: "white",
      turn: "black"
    };

    this.boardSize = 480;
    this.gridSize = this.boardSize / 8;

    this.newGame = this.newGame.bind(this);
    this.handleClick = this.handleClick.bind(this);
    this.changePlayer = this.changePlayer.bind(this);
  }

  changePlayer(e) {
    this.setState({
      humanPlayer: e.target.value,
      aiPlayer: this.opponent(e.target.value),
      turn: "black"
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
      js.gameStarted = true;
      js.action = "";
      js.gameId = guid();
      js.steps = [];
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
    this.drawAction(ctx);
  }

  drawAction(ctx) {
    if ("action" in this.state && this.state.action !== "") {
      var p = this.state.action;
      var r = p[0];
      var c = p[1];
      ctx.save();
      ctx.beginPath();
      ctx.arc((c + 0.5) * this.gridSize, (r + 0.5) * this.gridSize, this.gridSize / 2 - 1, 0, Math.PI * 2, false);
      ctx.closePath();
      ctx.lineWidth = 1;
      ctx.strokeStyle = "yellow";
      ctx.setLineDash([5, 3]);
      ctx.stroke();
      ctx.restore();
    }
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
    ctx.arc((c + 0.5) * this.gridSize, (r + 0.5) * this.gridSize, this.gridSize / 2 - 3, 0, Math.PI * 2, false);
    ctx.closePath();
    ctx.fillStyle = style;
    ctx.strokeStyle = style;
    ctx.fill();
    ctx.restore();
  }

  drawOptions(ctx) {
    for (var i = 0; i < this.state.options.length; i++) {
      var p = this.state.options[i];
      this.drawSinglePiece(ctx, p[0], p[1], 0);
    }
  }

  drawPieces(ctx) {
    for (var i = 0; i < 8; i++) {
      for (var j = 0; j < 8; j++) {
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
    ctx.strokeStyle = "#111";
    ctx.fillStye = "#111";
    ctx.beginPath();
    for (var i = 0; i <= 8; i++) {
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
    var c = parseInt((e.clientX - rect.left) / this.gridSize);
    var r = parseInt((e.clientY - rect.top) / this.gridSize);
    return {
      row: r,
      col: c
    };
  }

  handleClick(e) {
    var pos = this.getClickPosition(e);
    var c = pos.col;
    var r = pos.row;
    var validClick = false;
    for (var i = 0; i < this.state.options.length; i++) {
      var p = this.state.options[i];
      if (r === p[0] && c === p[1]) {
        validClick = true;
        break;
      }
    }

    if (validClick && this.state.turn === this.state.humanPlayer) {
      this.play({
        action: [r, c]
      });
    }
  }

  play(props) {
    if (this.state.gameStarted) {
      var formData = new FormData();
      if ("action" in props) {
        formData.append("data", JSON.stringify({
          player: this.state.turn,
          action: props["action"],
          board: this.state.board,
          gameId: this.state.gameId
        }));
      } else {
        formData.append("data", JSON.stringify({
          player: this.state.turn,
          board: this.state.board,
          gameId: this.state.gameId
        }));
      }

      fetch("/othello/play", {
        method: "post",
        body: formData
      }).then(response => {
        return response.json();
      }).then(js => {
        js.steps = JSON.parse(JSON.stringify(this.state.steps));
        js.steps.push({
          player: this.state.turn,
          action: js.action
        });
        this.setState(js);
      });
    }
  }

  render() {
    return (
      <div id="parent">
        <div id="board">
          <select onChange={this.changePlayer} disabled>
            <option value="black">Black</option>
            <option value="white">White</option>
          </select>
          <button onClick={this.newGame}>Start Game</button>
          <br/>
          Black Score: {this.state.blackScore}, White Score: {this.state.whiteScore}
          <br/>
          <canvas ref="board"
                  width={this.boardSize}
                  height={this.boardSize}
                  onClick={this.handleClick}/>
        </div>
        <div id="steps">
          {this.state.steps.map(s => <PlayRecordRow player={s.player} action={s.action}/>)}
        </div>
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
