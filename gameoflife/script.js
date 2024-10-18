const gridSize = 50;
let grid = [];
let nextGrid = [];
let stabilityCounter = [];
let intervalId;

const gridElement = document.getElementById('grid');
const startButton = document.getElementById('startButton');
const resetButton = document.getElementById('resetButton');
const messageElement = document.getElementById('message');

// グリッドを初期化し、ランダムに6つのセルを生存状態にする
function createGrid() {
  grid = [];
  nextGrid = [];
  stabilityCounter = [];
  gridElement.innerHTML = '';

  for (let row = 0; row < gridSize; row++) {
    const gridRow = [];
    const nextGridRow = [];
    const stabilityRow = [];
    for (let col = 0; col < gridSize; col++) {
      const cell = document.createElement('div');
      cell.classList.add('cell');
      cell.addEventListener('click', () => toggleCellState(row, col));
      gridElement.appendChild(cell);
      gridRow.push(0);
      nextGridRow.push(0);
      stabilityRow.push(0); // 安定性カウンタを初期化
    }
    grid.push(gridRow);
    nextGrid.push(nextGridRow);
    stabilityCounter.push(stabilityRow); // 安定性カウンタをグリッドに追加
  }

  // ランダムに中心の1つのセルとその周囲を選ぶ
  let centerRow = Math.floor(Math.random() * (gridSize - 2)) + 1; // 中心セルの行 (1～48の範囲)
  let centerCol = Math.floor(Math.random() * (gridSize - 2)) + 1; // 中心セルの列 (1～48の範囲)

  // 中心セルを生存状態にする
  grid[centerRow][centerCol] = 1;
  updateCell(centerRow, centerCol);

  // 周囲の8マスの中からランダムに5つ選ぶ
  const neighborOffsets = [
    [-1, -1], [-1, 0], [-1, 1],
    [0, -1],         [0, 1],
    [1, -1], [1, 0], [1, 1]
  ];

  // シャッフルして最初の5つを選択
  shuffleArray(neighborOffsets);
  for (let i = 0; i < 5; i++) {
    let [rowOffset, colOffset] = neighborOffsets[i];
    let newRow = centerRow + rowOffset;
    let newCol = centerCol + colOffset;
    grid[newRow][newCol] = 1; // 周囲セルを生存状態にする
    updateCell(newRow, newCol);
  }

  // メッセージをリセット
  messageElement.textContent = "生命(黒いセル)が残っている間あなたは休憩できます";
}

// 配列をシャッフルする関数（Fisher–Yatesアルゴリズム）
function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}

// セルの状態を切り替える
function toggleCellState(row, col) {
  grid[row][col] = grid[row][col] === 1 ? 0 : 1;
  updateCell(row, col);
}

// グリッドの描画を更新
function updateCell(row, col) {
  const cell = gridElement.children[row * gridSize + col];
  cell.classList.toggle('alive', grid[row][col] === 1);
}

// 次の世代の状態を計算
function calculateNextGeneration() {
  let aliveCount = 0;
  for (let row = 0; row < gridSize; row++) {
    for (let col = 0; col < gridSize; col++) {
      const aliveNeighbors = countAliveNeighbors(row, col);

      // セルの新しい状態を計算
      let newState = grid[row][col];
      if (grid[row][col] === 1) {
        // 生存ルール
        newState = aliveNeighbors === 2 || aliveNeighbors === 3 ? 1 : 0;
      } else {
        // 誕生ルール
        newState = aliveNeighbors === 3 ? 1 : 0;
      }

      // 状態が変わらない場合、安定性カウンタを増やす
      if (newState === grid[row][col]) {
        stabilityCounter[row][col]++;
      } else {
        stabilityCounter[row][col] = 0; // 状態が変わればカウンタをリセット
      }

      // 5ターン以上変化がないセルを強制的にdeadにする
      if (stabilityCounter[row][col] >= 5) {
        newState = 0;
      }

      nextGrid[row][col] = newState;

      // 生存セルのカウント
      if (newState === 1) {
        aliveCount++;
      }
    }
  }

  // グリッドを更新
  for (let row = 0; row < gridSize; row++) {
    for (let col = 0; col < gridSize; col++) {
      grid[row][col] = nextGrid[row][col];
      updateCell(row, col);  // 各セルの描画を更新
    }
  }

  // すべてのセルがdeadになった場合
  if (aliveCount === 0) {
    messageElement.textContent = "休憩終了";
  }
}

// 隣接する生存セルの数をカウント
function countAliveNeighbors(row, col) {
  let count = 0;
  for (let i = -1; i <= 1; i++) {
    for (let j = -1; j <= 1; j++) {
      if (i === 0 && j === 0) continue;
      const newRow = row + i;
      const newCol = col + j;
      if (newRow >= 0 && newRow < gridSize && newCol >= 0 && newCol < gridSize) {
        count += grid[newRow][newCol];
      }
    }
  }
  return count;
}

// ゲーム開始
function startGame() {
  if (!intervalId) {
    intervalId = setInterval(() => {
      calculateNextGeneration();
    }, 100);
  }
}

// ゲームリセット
function resetGame() {
  clearInterval(intervalId);
  intervalId = null;
  createGrid(); // リセット時にグリッドを再作成し、ランダムに6つのセルを黒くする
}

// イベントリスナー
startButton.addEventListener('click', startGame);
resetButton.addEventListener('click', resetGame);

// 初期グリッド作成
createGrid();
