# -*- coding: utf-8 -*-
"""课程内容与题库种子数据。

拆分为独立模块便于维护：
- LESSONS：课程学习内容（结构化 HTML，支持 MathJax 公式）
- QUESTIONS：题库（单选 / 多选 / 判断 / 填空，三种难度）
"""

# --------------------------------------------------------------------------
# 课程学习内容：每个章节 3 个课节，含学习目标、知识要点、典型例题、小结
# --------------------------------------------------------------------------
LESSONS = [
    # ================= 第 1 章 函数与极限 =================
    (1, "1.1 函数的概念与性质", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>理解函数的概念，会求函数的定义域与值域；</li>
  <li>掌握函数的四种基本性质：有界性、单调性、奇偶性、周期性；</li>
  <li>熟悉基本初等函数与复合函数、反函数的构造。</li>
</ul></div>

<h4>一、函数的概念</h4>
<p>设 \\(D\\) 为非空实数集，若对每个 \\(x\\in D\\)，按对应法则 \\(f\\) 都有唯一确定的实数 \\(y\\) 与之对应，则称 \\(f\\) 为定义在 \\(D\\) 上的函数，记作 \\(y=f(x),\\ x\\in D\\)，其中 \\(D\\) 称为定义域，集合 \\(\\{y\\mid y=f(x),x\\in D\\}\\) 称为值域。</p>
<div class="lesson-box tip"><strong>求定义域的三个约束：</strong>
① 分式的分母不为零；② 偶次根式的被开方数非负；③ 对数函数的真数大于零。
例如 \\(f(x)=\\dfrac{\\sqrt{x-1}}{\\ln(3-x)}\\) 的定义域为 \\([1,2)\\cup(2,3)\\)。</div>

<h4>二、函数的四种性质</h4>
<ul>
  <li><strong>有界性：</strong>若存在 \\(M>0\\)，使 \\(|f(x)|\\le M\\) 对一切 \\(x\\in D\\) 成立，则称 \\(f\\) 在 \\(D\\) 上有界。</li>
  <li><strong>单调性：</strong>任取 \\(x_1<x_2\\)，若 \\(f(x_1)<f(x_2)\\) 则单调递增；反之单调递减。</li>
  <li><strong>奇偶性：</strong>定义域关于原点对称时，\\(f(-x)=f(x)\\) 为偶函数（图象关于 \\(y\\) 轴对称），\\(f(-x)=-f(x)\\) 为奇函数（图象关于原点对称）。</li>
  <li><strong>周期性：</strong>若存在 \\(T>0\\)，使 \\(f(x+T)=f(x)\\) 恒成立，则 \\(T\\) 为周期。</li>
</ul>

<h4>三、基本初等函数</h4>
<p>幂函数 \\(y=x^a\\)、指数函数 \\(y=a^x\\,(a>0,a\\ne1)\\)、对数函数 \\(y=\\log_a x\\)、三角函数与反三角函数，统称基本初等函数。由它们经有限次四则运算与复合所构成的函数称为初等函数。</p>

<h4>四、典型例题</h4>
<div class="lesson-example"><p><strong>例 1</strong> 设 \\(f(x)=x^2+1\\)，求 \\(f(x+1)\\)。</p>
<p><strong>解：</strong>把 \\(x+1\\) 代入自变量位置，\\(f(x+1)=(x+1)^2+1=x^2+2x+2\\)。</p></div>
<div class="lesson-example"><p><strong>例 2</strong> 判断 \\(f(x)=x^3+x\\) 的奇偶性。</p>
<p><strong>解：</strong>定义域为 \\(\\mathbb{R}\\)，关于原点对称，且 \\(f(-x)=(-x)^3+(-x)=-x^3-x=-f(x)\\)，故为奇函数。</p></div>

<div class="lesson-box"><strong>本节小结：</strong>函数问题的第一步永远是"看定义域"；判断奇偶性必须先验证定义域是否关于原点对称。</div>
"""),

    (1, "1.2 数列与函数的极限", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>理解数列极限与函数极限的 \\(\\varepsilon\\)-\\(N\\)、\\(\\varepsilon\\)-\\(\\delta\\) 定义；</li>
  <li>掌握两个重要极限并能灵活运用；</li>
  <li>理解左极限、右极限与极限存在的关系。</li>
</ul></div>

<h4>一、极限的定义</h4>
<p>数列极限：\\(\\lim\\limits_{n\\to\\infty}x_n=a\\) 指当 \\(n\\) 充分大时 \\(x_n\\) 与 \\(a\\) 任意接近。函数极限：\\(\\lim\\limits_{x\\to x_0}f(x)=A\\) 指当 \\(x\\) 充分接近 \\(x_0\\)（但不等于 \\(x_0\\)）时 \\(f(x)\\) 任意接近 \\(A\\)。</p>
<p>极限存在的充要条件是左右极限存在且相等：\\(\\lim\\limits_{x\\to x_0}f(x)=A\\iff f(x_0^-)=f(x_0^+)=A\\)。</p>

<h4>二、两个重要极限</h4>
<div class="lesson-box">
<p>① \\(\\lim\\limits_{x\\to 0}\\dfrac{\\sin x}{x}=1\\)（\\(0/0\\) 型三角极限）</p>
<p>② \\(\\lim\\limits_{x\\to\\infty}\\left(1+\\dfrac{1}{x}\\right)^x=e\\)，等价形式 \\(\\lim\\limits_{x\\to 0}(1+x)^{\\frac{1}{x}}=e\\)（\\(1^\\infty\\) 型）</p>
</div>

<h4>三、典型例题</h4>
<div class="lesson-example"><p><strong>例 1</strong> 求 \\(\\lim\\limits_{x\\to 0}\\dfrac{\\sin 3x}{x}\\)。</p>
<p><strong>解：</strong>凑重要极限形式：
\\(\\lim\\limits_{x\\to 0}\\dfrac{\\sin 3x}{x}=\\lim\\limits_{x\\to 0}3\\cdot\\dfrac{\\sin 3x}{3x}=3\\times 1=3\\)。</p></div>
<div class="lesson-example"><p><strong>例 2</strong> 求 \\(\\lim\\limits_{x\\to\\infty}\\left(1+\\dfrac{2}{x}\\right)^{x}\\)。</p>
<p><strong>解：</strong>令 \\(u=\\dfrac{x}{2}\\)，则 \\(\\left(1+\\dfrac{2}{x}\\right)^x=\\left[\\left(1+\\frac{1}{u}\\right)^{u}\\right]^{2}\\to e^{2}\\)。</p></div>

<div class="lesson-box tip"><strong>易错提醒：</strong>重要极限中的"变量替换"必须整体一致，\\(\\sin 3x\\sim 3x\\) 只能用于乘除结构，加减结构中不能随意替换。</div>
"""),

    (1, "1.3 无穷小、无穷大与极限运算法则", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>理解无穷小与无穷大的概念及其关系；</li>
  <li>掌握极限的四则运算法则与复合运算法则；</li>
  <li>会用等价无穷小替换与夹逼准则求极限。</li>
</ul></div>

<h4>一、无穷小与无穷大</h4>
<p>若 \\(\\lim\\limits_{x\\to x_0}f(x)=0\\)，则称 \\(f(x)\\) 为该极限过程中的无穷小。性质：有限个无穷小之和仍为无穷小；无穷小与有界函数的乘积仍为无穷小。</p>
<p>在同一过程中，若 \\(|f(x)|\\) 无限增大，则称 \\(f(x)\\) 为无穷大，记作 \\(\\lim f(x)=\\infty\\)。无穷大的倒数（非零处）是无穷小。</p>

<h4>二、常用等价无穷小（\\(x\\to 0\\)）</h4>
<div class="lesson-box">
\\(\\sin x\\sim x,\\quad \\tan x\\sim x,\\quad \\arcsin x\\sim x,\\quad \\arctan x\\sim x,\\)
\\(\\ln(1+x)\\sim x,\\quad e^{x}-1\\sim x,\\quad 1-\\cos x\\sim\\dfrac{x^2}{2},\\quad (1+x)^{\\alpha}-1\\sim \\alpha x\\)
</div>

<h4>三、极限运算法则</h4>
<p>若 \\(\\lim f=A,\\ \\lim g=B\\)（均为有限数），则 \\(\\lim(f\\pm g)=A\\pm B\\)，\\(\\lim(fg)=AB\\)，当 \\(B\\ne 0\\) 时 \\(\\lim\\dfrac{f}{g}=\\dfrac{A}{B}\\)。</p>
<div class="lesson-box tip"><strong>求解极限的通法：</strong>先判断类型（\\(\\frac{0}{0}\\)、\\(\\frac{\\infty}{\\infty}\\)、\\(\\infty-\\infty\\)、\\(1^\\infty\\)）→ 再选方法（约分、通分、有理化、等价无穷小、洛必达法则、重要极限）。</div>

<h4>四、典型例题</h4>
<div class="lesson-example"><p><strong>例</strong> 求 \\(\\lim\\limits_{x\\to 0}\\dfrac{e^{x}-1}{\\sin 2x}\\)。</p>
<p><strong>解：</strong>由等价无穷小 \\(e^x-1\\sim x,\\ \\sin 2x\\sim 2x\\)，故原式 \\(=\\lim\\limits_{x\\to0}\\dfrac{x}{2x}=\\dfrac{1}{2}\\)。</p></div>

<div class="lesson-box"><strong>本节小结：</strong>等价无穷小替换是求 \\(0/0\\) 型极限最快的工具，但只适用于乘除因子，遇到加减结构需先变形。</div>
"""),

    # ================= 第 2 章 导数与微分 =================
    (2, "2.1 导数的概念", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>理解导数作为变化率与切线斜率的双重含义；</li>
  <li>会用定义求导数，掌握可导与连续的关系；</li>
  <li>了解左导数、右导数与分段函数在分界点的可导性判定。</li>
</ul></div>

<h4>一、导数的定义</h4>
<p>\\(f'(x_0)=\\lim\\limits_{\\Delta x\\to 0}\\dfrac{f(x_0+\\Delta x)-f(x_0)}{\\Delta x}\\)，也可写作 \\(\\lim\\limits_{x\\to x_0}\\dfrac{f(x)-f(x_0)}{x-x_0}\\)。</p>
<p><strong>几何意义：</strong>\\(f'(x_0)\\) 是曲线 \\(y=f(x)\\) 在点 \\((x_0,f(x_0))\\) 处切线的斜率，切线方程 \\(y-f(x_0)=f'(x_0)(x-x_0)\\)。</p>
<p><strong>物理意义：</strong>位移对时间的导数即瞬时速度，速度对时间的导数即加速度。</p>

<h4>二、可导与连续的关系</h4>
<div class="lesson-box tip">可导必连续，连续不一定可导。典型反例：\\(y=|x|\\) 在 \\(x=0\\) 处连续但左右导数分别为 \\(-1\\) 与 \\(1\\)，故不可导。</div>

<h4>三、典型例题</h4>
<div class="lesson-example"><p><strong>例 1</strong> 用定义求 \\(f(x)=x^2\\) 在 \\(x=1\\) 处的导数。</p>
<p><strong>解：</strong>\\(f'(1)=\\lim\\limits_{\\Delta x\\to0}\\dfrac{(1+\\Delta x)^2-1^2}{\\Delta x}=\\lim\\limits_{\\Delta x\\to0}(2+\\Delta x)=2\\)。</p></div>
<div class="lesson-example"><p><strong>例 2</strong> 求曲线 \\(y=x^2\\) 在点 \\((1,1)\\) 处的切线方程。</p>
<p><strong>解：</strong>斜率 \\(k=y'\\big|_{x=1}=2\\)，切线方程 \\(y-1=2(x-1)\\)，即 \\(y=2x-1\\)。</p></div>
"""),

    (2, "2.2 求导法则与复合函数求导", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>熟记基本初等函数的导数公式；</li>
  <li>掌握四则运算求导法则与链式法则；</li>
  <li>会求隐函数的导数。</li>
</ul></div>

<h4>一、基本导数公式</h4>
<div class="lesson-box">
\\((x^n)'=nx^{n-1},\\quad (\\sin x)'=\\cos x,\\quad (\\cos x)'=-\\sin x,\\)
\\((e^x)'=e^x,\\quad (a^x)'=a^x\\ln a,\\quad (\\ln x)'=\\dfrac{1}{x},\\quad (\\log_a x)'=\\dfrac{1}{x\\ln a}\\)</div>

<h4>二、四则运算与链式法则</h4>
<p>\\((u\\pm v)'=u'\\pm v',\\quad (uv)'=u'v+uv',\\quad \\left(\\dfrac{u}{v}\\right)'=\\dfrac{u'v-uv'}{v^{2}}\\)</p>
<p>链式法则（复合函数）：\\(\\dfrac{dy}{dx}=\\dfrac{dy}{du}\\cdot\\dfrac{du}{dx}\\)，即"外层导数 × 内层导数"。</p>

<h4>三、典型例题</h4>
<div class="lesson-example"><p><strong>例 1</strong> 求 \\(y=\\sin(3x^2+1)\\) 的导数。</p>
<p><strong>解：</strong>\\(y'=\\cos(3x^2+1)\\cdot(3x^2+1)'=6x\\cos(3x^2+1)\\)。</p></div>
<div class="lesson-example"><p><strong>例 2</strong> 求 \\(y=x^2e^{x}\\) 的导数。</p>
<p><strong>解：</strong>用乘积法则 \\(y'=2xe^{x}+x^2e^{x}=xe^x(2+x)\\)。</p></div>
<div class="lesson-example"><p><strong>例 3</strong> 求由方程 \\(x^2+y^2=1\\) 确定的隐函数 \\(y=y(x)\\) 的导数。</p>
<p><strong>解：</strong>两边对 \\(x\\) 求导得 \\(2x+2yy'=0\\)，故 \\(y'=-\\dfrac{x}{y}\\ (y\\ne0)\\)。</p></div>

<div class="lesson-box tip"><strong>易错提醒：</strong>链式法则千万别漏掉内层导数 \\((\\sin 3x)'=3\\cos 3x\\)，而不是 \\(\\cos 3x\\)。</div>
"""),

    (2, "2.3 高阶导数与微分", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>理解高阶导数的概念与记号；</li>
  <li>掌握微分的定义、几何意义与不变性；</li>
  <li>会用微分做近似计算。</li>
</ul></div>

<h4>一、高阶导数</h4>
<p>\\(y''=(y')'\\) 称为二阶导数，类似地有 \\(n\\) 阶导数 \\(y^{(n)}\\)。常用结果：\\((e^x)^{(n)}=e^x\\)，\\((\\sin x)^{(n)}=\\sin\\left(x+\\dfrac{n\\pi}{2}\\right)\\)，\\((x^n)^{(n)}=n!\\)。</p>

<h4>二、微分</h4>
<p>\\(dy=f'(x)dx\\)，其中 \\(dx=\\Delta x\\)。几何意义：\\(dy\\) 是切线纵坐标的增量，\\(\\Delta y\\) 是曲线纵坐标的增量，\\(\\Delta y\\approx dy\\)（\\(|\\Delta x|\\) 很小时）。</p>
<p><strong>近似公式：</strong>\\(f(x_0+\\Delta x)\\approx f(x_0)+f'(x_0)\\Delta x\\)。例如 \\(\\sqrt{1.02}\\approx1+\\dfrac{1}{2}\\times0.02=1.01\\)。</p>

<h4>三、典型例题</h4>
<div class="lesson-example"><p><strong>例</strong> 设 \\(y=e^{2x}\\)，求 \\(dy\\)。</p>
<p><strong>解：</strong>\\(y'=2e^{2x}\\)，故 \\(dy=2e^{2x}dx\\)。</p></div>
"""),

    # ================= 第 3 章 中值定理与导数应用 =================
    (3, "3.1 微分中值定理", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>理解罗尔定理、拉格朗日中值定理、柯西中值定理的条件与结论；</li>
  <li>会用中值定理证明恒等式与不等式。</li>
</ul></div>

<h4>一、罗尔定理</h4>
<p>若 \\(f\\) 在 \\([a,b]\\) 上连续、在 \\((a,b)\\) 内可导，且 \\(f(a)=f(b)\\)，则存在 \\(\\xi\\in(a,b)\\)，使 \\(f'(\\xi)=0\\)。</p>

<h4>二、拉格朗日中值定理</h4>
<div class="lesson-box">\\(f(b)-f(a)=f'(\\xi)(b-a),\\quad \\xi\\in(a,b)\\)</div>
<p>它表明"函数在两个点上的平均变化率等于某点处的瞬时变化率"，是微分学最重要的桥梁。</p>

<h4>三、柯西中值定理</h4>
<p>若 \\(f,g\\) 满足相应条件且 \\(g'(x)\\ne0\\)，则 \\(\\dfrac{f(b)-f(a)}{g(b)-g(a)}=\\dfrac{f'(\\xi)}{g'(\\xi)}\\)。</p>

<h4>四、典型例题</h4>
<div class="lesson-example"><p><strong>例</strong> 证明：当 \\(x>0\\) 时 \\(\\ln(1+x)<x\\)。</p>
<p><strong>解：</strong>令 \\(f(t)=\\ln(1+t)\\)，在 \\([0,x]\\) 上用拉格朗日中值定理，存在 \\(\\xi\\in(0,x)\\) 使
\\(\\ln(1+x)-\\ln 1=\\dfrac{x}{1+\\xi}\\)。因 \\(\\xi>0\\)，故 \\(\\dfrac{x}{1+\\xi}<x\\)，即 \\(\\ln(1+x)<x\\)。</p></div>
"""),

    (3, "3.2 洛必达法则", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>掌握 \\(\\frac{0}{0}\\) 与 \\(\\frac{\\infty}{\\infty}\\) 型不定式的洛必达法则；</li>
  <li>会把 \\(0\\cdot\\infty\\)、\\(\\infty-\\infty\\)、\\(1^\\infty\\) 型转化为基本型。</li>
</ul></div>

<h4>一、基本形式</h4>
<p>若 \\(\\lim\\dfrac{f(x)}{g(x)}\\) 为 \\(\\dfrac{0}{0}\\) 或 \\(\\dfrac{\\infty}{\\infty}\\) 型，且 \\(\\lim\\dfrac{f'(x)}{g'(x)}\\) 存在（或为无穷大），则
\\(\\lim\\dfrac{f(x)}{g(x)}=\\lim\\dfrac{f'(x)}{g'(x)}\\)。</p>

<h4>二、其他类型的转化</h4>
<ul>
  <li>\\(0\\cdot\\infty\\)：化为 \\(\\dfrac{0}{1/\\infty}\\) 或 \\(\\dfrac{\\infty}{1/0}\\)；</li>
  <li>\\(\\infty-\\infty\\)：通分或有理化后化为商式；</li>
  <li>\\(1^\\infty,\\ 0^0,\\ \\infty^0\\)：取对数后用 \\(0\\cdot\\infty\\) 型处理。</li>
</ul>

<h4>三、典型例题</h4>
<div class="lesson-example"><p><strong>例 1</strong> 求 \\(\\lim\\limits_{x\\to0}\\dfrac{e^x-1}{x}\\)。</p>
<p><strong>解：</strong>\\(\\dfrac{0}{0}\\) 型，用洛必达法则得 \\(\\lim\\limits_{x\\to0}\\dfrac{e^x}{1}=1\\)。</p></div>
<div class="lesson-example"><p><strong>例 2</strong> 求 \\(\\lim\\limits_{x\\to\\infty}\\dfrac{\\ln x}{x}\\)。</p>
<p><strong>解：</strong>\\(\\dfrac{\\infty}{\\infty}\\) 型，\\(\\lim\\limits_{x\\to\\infty}\\dfrac{1/x}{1}=0\\)。</p></div>

<div class="lesson-box tip"><strong>易错提醒：</strong>洛必达法则不是万能的，只有满足"不定式 + 导数之比极限存在"才能用；能靠等价无穷小解决的题优先用等价无穷小。</div>
"""),

    (3, "3.3 单调性、极值与最值", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>会用一阶导数判定单调性与极值；</li>
  <li>会用二阶导数判定凹凸性与拐点；</li>
  <li>会求闭区间上连续函数的最值。</li>
</ul></div>

<h4>一、单调性与极值</h4>
<p>在区间内若 \\(f'(x)>0\\) 则函数单调递增，\\(f'(x)<0\\) 则单调递减。极值点只能出现在驻点（\\(f'(x)=0\\)）或不可导点处。</p>
<p><strong>第一充分条件：</strong>\\(f'\\) 在 \\(x_0\\) 左右由正变负 → 极大值；由负变正 → 极小值。<br>
<strong>第二充分条件：</strong>\\(f'(x_0)=0\\) 且 \\(f''(x_0)<0\\) → 极大值；\\(f''(x_0)>0\\) → 极小值。</p>

<h4>二、凹凸性与拐点</h4>
<p>\\(f''(x)>0\\) 曲线凹（下凸），\\(f''(x)<0\\) 曲线凸（上凸）；\\(f''\\) 变号处为拐点。</p>

<h4>三、最值的求法</h4>
<div class="lesson-box">闭区间 \\([a,b]\\) 上连续函数的最值：比较所有驻点、不可导点及端点处的函数值，取最大与最小者。</div>

<h4>四、典型例题</h4>
<div class="lesson-example"><p><strong>例</strong> 求 \\(f(x)=x^3-3x\\) 的极值。</p>
<p><strong>解：</strong>\\(f'(x)=3x^2-3=3(x-1)(x+1)\\)，驻点为 \\(x=\\pm1\\)。
\\(f''(x)=6x\\)，\\(f''(1)=6>0\\) 故 \\(x=1\\) 为极小值点，极小值 \\(f(1)=-2\\)；
\\(f''(-1)=-6<0\\) 故 \\(x=-1\\) 为极大值点，极大值 \\(f(-1)=2\\)。</p></div>
"""),

    # ================= 第 4 章 不定积分 =================
    (4, "4.1 不定积分的概念与基本公式", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>理解原函数与不定积分的概念，掌握积分常数 C 的意义；</li>
  <li>熟记基本积分公式表；</li>
  <li>掌握不定积分的线性性质。</li>
</ul></div>

<h4>一、原函数与不定积分</h4>
<p>若 \\(F'(x)=f(x)\\)，则称 \\(F(x)\\) 是 \\(f(x)\\) 的一个原函数，全体原函数记作
\\(\\int f(x)\\,dx=F(x)+C\\)，其中 \\(C\\) 为任意常数。</p>

<h4>二、基本积分公式</h4>
<div class="lesson-box">
\\(\\int x^{\\alpha}dx=\\dfrac{x^{\\alpha+1}}{\\alpha+1}+C\\ (\\alpha\\ne-1),\\quad \\int\\dfrac{1}{x}dx=\\ln|x|+C,\\)
\\(\\int e^{x}dx=e^{x}+C,\\quad \\int a^{x}dx=\\dfrac{a^{x}}{\\ln a}+C,\\)
\\(\\int\\cos x\\,dx=\\sin x+C,\\quad \\int\\sin x\\,dx=-\\cos x+C,\\quad \\int\\dfrac{dx}{1+x^{2}}=\\arctan x+C\\)</div>

<h4>三、线性性质</h4>
<p>\\(\\int[\\alpha f(x)+\\beta g(x)]dx=\\alpha\\int f(x)dx+\\beta\\int g(x)dx\\)。</p>

<h4>四、典型例题</h4>
<div class="lesson-example"><p><strong>例</strong> 求 \\(\\int\\left(3x^{2}+\\dfrac{1}{x}\\right)dx\\)。</p>
<p><strong>解：</strong>\\(=3\\cdot\\dfrac{x^{3}}{3}+\\ln|x|+C=x^{3}+\\ln|x|+C\\)。</p></div>

<div class="lesson-box tip"><strong>易错提醒：</strong>积分结果千万不要漏写 \\(+C\\)；\\(\\int\\frac{1}{x}dx\\) 的结果带绝对值 \\(\\ln|x|+C\\)。</div>
"""),

    (4, "4.2 换元积分法", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>掌握第一类换元法（凑微分法）与第二类换元法；</li>
  <li>会用三角代换处理含根式的积分。</li>
</ul></div>

<h4>一、第一类换元法（凑微分）</h4>
<div class="lesson-box">\\(\\int f[\\varphi(x)]\\varphi'(x)dx=\\int f(u)du\\Big|_{u=\\varphi(x)}\\)</div>
<p>关键是识别"某个函数的导数恰好出现在被积表达式中"。常用凑法：
\\(x\\,dx=\\dfrac{1}{2}d(x^{2}),\\quad \\dfrac{dx}{x}=d\\ln x,\\quad e^{x}dx=de^{x}\\)。</p>

<h4>二、第二类换元法</h4>
<p>当被积函数含根式时，作变量替换去掉根号：</p>
<ul>
  <li>\\(\\sqrt{a^{2}-x^{2}}\\)：令 \\(x=a\\sin t\\)；</li>
  <li>\\(\\sqrt{a^{2}+x^{2}}\\)：令 \\(x=a\\tan t\\)；</li>
  <li>\\(\\sqrt{x^{2}-a^{2}}\\)：令 \\(x=a\\sec t\\)。</li>
</ul>

<h4>三、典型例题</h4>
<div class="lesson-example"><p><strong>例 1</strong> 求 \\(\\int 2x\\cos(x^{2})dx\\)。</p>
<p><strong>解：</strong>注意到 \\(2xdx=d(x^{2})\\)，令 \\(u=x^{2}\\)，则原式 \\(=\\int\\cos u\\,du=\\sin u+C=\\sin(x^{2})+C\\)。</p></div>
<div class="lesson-example"><p><strong>例 2</strong> 求 \\(\\int\\dfrac{dx}{1+x^{2}}\\)（直接套用公式）与 \\(\\int\\dfrac{2x}{1+x^{2}}dx\\)。</p>
<p><strong>解：</strong>前者为 \\(\\arctan x+C\\)；后者凑微分 \\(d(1+x^2)=2xdx\\)，得 \\(\\ln(1+x^{2})+C\\)。</p></div>
"""),

    (4, "4.3 分部积分法", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>掌握分部积分公式的推导与运用；</li>
  <li>会按"反对幂指三"的顺序选择 \\(u\\)。</li>
</ul></div>

<h4>一、分部积分公式</h4>
<div class="lesson-box">\\(\\int u\\,dv=uv-\\int v\\,du\\)</div>

<h4>二、\\(u\\) 的选取顺序</h4>
<p>口诀"<strong>反、对、幂、指、三</strong>"：反三角函数 &gt; 对数函数 &gt; 幂函数 &gt; 指数函数 &gt; 三角函数，排在前面的优先取作 \\(u\\)。</p>

<h4>三、典型例题</h4>
<div class="lesson-example"><p><strong>例 1</strong> 求 \\(\\int x\\,e^{x}dx\\)。</p>
<p><strong>解：</strong>取 \\(u=x,\\ dv=e^{x}dx\\)，则 \\(du=dx,\\ v=e^{x}\\)，故
\\(\\int xe^{x}dx=xe^{x}-\\int e^{x}dx=xe^{x}-e^{x}+C\\)。</p></div>
<div class="lesson-example"><p><strong>例 2</strong> 求 \\(\\int x\\ln x\\,dx\\)。</p>
<p><strong>解：</strong>取 \\(u=\\ln x,\\ dv=xdx\\)，则
\\(\\int x\\ln x\\,dx=\\dfrac{x^{2}}{2}\\ln x-\\int\\dfrac{x}{2}dx=\\dfrac{x^{2}}{2}\\ln x-\\dfrac{x^{2}}{4}+C\\)。</p></div>
"""),

    # ================= 第 5 章 定积分及其应用 =================
    (5, "5.1 定积分的概念与性质", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>理解定积分作为"和式极限"的本质与几何意义；</li>
  <li>掌握定积分的基本性质与积分中值定理；</li>
  <li>掌握变限积分函数及其求导公式。</li>
</ul></div>

<h4>一、定积分的定义</h4>
<p>\\(\\int_{a}^{b}f(x)dx=\\lim\\limits_{\\lambda\\to0}\\sum\\limits_{i=1}^{n}f(\\xi_i)\\Delta x_i\\)，几何上表示曲线 \\(y=f(x)\\) 与 \\(x\\) 轴所围曲边梯形的面积代数和。</p>

<h4>二、基本性质</h4>
<ul>
  <li>\\(\\int_{a}^{b}[f\\pm g]dx=\\int_a^b f\\,dx\\pm\\int_a^b g\\,dx\\)；</li>
  <li>\\(\\int_{a}^{b}f\\,dx=-\\int_{b}^{a}f\\,dx\\)，\\(\\int_a^a f\\,dx=0\\)；</li>
  <li>奇函数在对称区间上积分为 0：\\(\\int_{-a}^{a}f\\,dx=0\\)；偶函数则等于两倍半区间积分。</li>
</ul>

<h4>三、变限积分与求导</h4>
<div class="lesson-box">\\(\\Phi(x)=\\int_{a}^{x}f(t)dt\\ \\Rightarrow\\ \\Phi'(x)=f(x)\\)；\\(\\dfrac{d}{dx}\\int_{a}^{\\varphi(x)}f(t)dt=f[\\varphi(x)]\\varphi'(x)\\)</div>

<h4>四、典型例题</h4>
<div class="lesson-example"><p><strong>例</strong> 求 \\(\\dfrac{d}{dx}\\int_{0}^{x}\\sin t\\,dt\\)。</p>
<p><strong>解：</strong>由变限积分求导公式，结果为被积函数在 \\(x\\) 处的值，即 \\(\\sin x\\)。</p></div>
"""),

    (5, "5.2 牛顿-莱布尼茨公式", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>理解微积分基本定理的意义；</li>
  <li>能用牛顿-莱布尼茨公式计算定积分；</li>
  <li>会用定积分处理简单几何与物理问题。</li>
</ul></div>

<h4>一、微积分基本定理</h4>
<div class="lesson-box">若 \\(F'(x)=f(x)\\) 且 \\(f\\) 在 \\([a,b]\\) 上连续，则 \\(\\int_{a}^{b}f(x)dx=F(b)-F(a)\\)。</div>
<p>它把"求面积的和式极限"转化为"求原函数并作差"，是微积分中最核心的公式。</p>

<h4>二、典型例题</h4>
<div class="lesson-example"><p><strong>例 1</strong> 计算 \\(\\int_{0}^{1}x\\,dx\\)。</p>
<p><strong>解：</strong>原函数为 \\(\\dfrac{x^{2}}{2}\\)，故 \\(\\int_{0}^{1}xdx=\\dfrac{1}{2}-0=\\dfrac{1}{2}\\)。</p></div>
<div class="lesson-example"><p><strong>例 2</strong> 计算 \\(\\int_{0}^{\\pi}\\sin x\\,dx\\)。</p>
<p><strong>解：</strong>原函数为 \\(-\\cos x\\)，\\(\\int_{0}^{\\pi}\\sin xdx=-\\cos\\pi+\\cos0=1+1=2\\)。</p></div>
<div class="lesson-example"><p><strong>例 3</strong> 计算 \\(\\int_{1}^{e}\\dfrac{1}{x}dx\\)。</p>
<p><strong>解：</strong>\\([\\ln|x|]_{1}^{e}=\\ln e-\\ln 1=1\\)。</p></div>
"""),

    (5, "5.3 定积分的应用", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>会用定积分求平面图形的面积与旋转体的体积；</li>
  <li>会用定积分解决变力做功、液体压力等物理问题；</li>
  <li>掌握"微元法"的分析思路。</li>
</ul></div>

<h4>一、微元法思路</h4>
<p>把待求量分解为"在小区间上近似不变"的微元，再积分求和：\\(Q=\\int_{a}^{b}dQ\\)。</p>

<h4>二、常用公式</h4>
<div class="lesson-box">
平面图形面积：\\(S=\\int_{a}^{b}[f(x)-g(x)]dx\\)<br>
绕 \\(x\\) 轴旋转体体积：\\(V=\\pi\\int_{a}^{b}f^{2}(x)dx\\)<br>
变力做功：\\(W=\\int_{a}^{b}F(x)dx\\)</div>

<h4>三、典型例题</h4>
<div class="lesson-example"><p><strong>例</strong> 求由 \\(y=x^{2}\\) 与 \\(y=x\\) 所围图形的面积。</p>
<p><strong>解：</strong>两曲线交于 \\((0,0)\\) 与 \\((1,1)\\)，在 \\([0,1]\\) 上 \\(x\\ge x^{2}\\)，故
\\(S=\\int_{0}^{1}(x-x^{2})dx=\\dfrac{1}{2}-\\dfrac{1}{3}=\\dfrac{1}{6}\\)。</p></div>
"""),

    # ================= 第 6 章 常微分方程 =================
    (6, "6.1 微分方程的基本概念与可分离变量方程", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>理解微分方程的阶、通解、特解与初始条件；</li>
  <li>掌握可分离变量方程的解法。</li>
</ul></div>

<h4>一、基本概念</h4>
<p>含有未知函数及其导数的方程称为微分方程；未知函数最高阶导数的阶数称为方程的阶。含任意常数且个数等于阶数的解称为通解，给初始条件确定常数后的解称为特解。</p>

<h4>二、可分离变量方程</h4>
<div class="lesson-box">形如 \\(\\dfrac{dy}{dx}=f(x)g(y)\\) 的方程，可化为 \\(\\dfrac{dy}{g(y)}=f(x)dx\\)，两边分别积分求解。</div>

<h4>三、典型例题</h4>
<div class="lesson-example"><p><strong>例 1</strong> 求 \\(y'=y\\) 的通解。</p>
<p><strong>解：</strong>分离变量 \\(\\dfrac{dy}{y}=dx\\)，积分得 \\(\\ln|y|=x+C_1\\)，故通解 \\(y=Ce^{x}\\)。</p></div>
<div class="lesson-example"><p><strong>例 2</strong> 求 \\(y'=3x^{2}\\) 满足 \\(y(0)=1\\) 的特解。</p>
<p><strong>解：</strong>两边积分得 \\(y=x^{3}+C\\)，代入 \\(y(0)=1\\) 得 \\(C=1\\)，故特解 \\(y=x^{3}+1\\)。</p></div>
"""),

    (6, "6.2 一阶线性微分方程", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>识别一阶线性微分方程的标准形式；</li>
  <li>掌握常数变易法推导的通解公式并能直接套用。</li>
</ul></div>

<h4>一、标准形式与通解公式</h4>
<div class="lesson-box">\\(y'+P(x)y=Q(x)\\ \\Longrightarrow\\ y=e^{-\\int P dx}\\left[\\int Q(x)e^{\\int P dx}dx+C\\right]\\)</div>
<p>当 \\(Q(x)\\equiv0\\) 时为齐次方程，通解为 \\(y=Ce^{-\\int Pdx}\\)。</p>

<h4>二、典型例题</h4>
<div class="lesson-example"><p><strong>例</strong> 求 \\(y'+y=e^{x}\\) 的通解。</p>
<p><strong>解：</strong>此处 \\(P=1,Q=e^{x}\\)，先求积分因子 \\(e^{\\int 1dx}=e^{x}\\)，两边同乘以 \\(e^{x}\\)：
\\((ye^{x})'=e^{2x}\\)，积分得 \\(ye^{x}=\\dfrac{1}{2}e^{2x}+C\\)，故 \\(y=\\dfrac{1}{2}e^{x}+Ce^{-x}\\)。</p></div>

<div class="lesson-box tip"><strong>易错提醒：</strong>使用公式前必须把方程整理成 \\(y'+P(x)y=Q(x)\\) 的标准形式，且 \\(y'\\) 的系数为 1。</div>
"""),

    (6, "6.3 二阶常系数线性微分方程", """
<div class="lesson-goal"><h4>学习目标</h4>
<ul>
  <li>掌握二阶常系数齐次线性方程的特征方程解法；</li>
  <li>会根据特征根的不同情况写出通解。</li>
</ul></div>

<h4>一、特征方程与三种情形</h4>
<p>方程 \\(y''+py'+qy=0\\) 的特征方程为 \\(r^{2}+pr+q=0\\)，设其判别式 \\(\\Delta=p^{2}-4q\\)。</p>
<div class="lesson-box">
① \\(\\Delta>0\\)：两个不等实根 \\(r_1,r_2\\)，通解 \\(y=C_1e^{r_1x}+C_2e^{r_2x}\\)<br>
② \\(\\Delta=0\\)：重根 \\(r\\)，通解 \\(y=(C_1+C_2x)e^{rx}\\)<br>
③ \\(\\Delta<0\\)：共轭复根 \\(\\alpha\\pm\\beta i\\)，通解 \\(y=e^{\\alpha x}(C_1\\cos\\beta x+C_2\\sin\\beta x)\\)</div>

<h4>二、典型例题</h4>
<div class="lesson-example"><p><strong>例 1</strong> 求 \\(y''-3y'+2y=0\\) 的通解。</p>
<p><strong>解：</strong>特征方程 \\(r^{2}-3r+2=0\\)，解得 \\(r_1=1,\\ r_2=2\\)，故通解 \\(y=C_1e^{x}+C_2e^{2x}\\)。</p></div>
<div class="lesson-example"><p><strong>例 2</strong> 求 \\(y''+y=0\\) 的通解。</p>
<p><strong>解：</strong>特征根为 \\(r=\\pm i\\)，即 \\(\\alpha=0,\\beta=1\\)，故 \\(y=C_1\\cos x+C_2\\sin x\\)。</p></div>
"""),
]


# --------------------------------------------------------------------------
# 题库：(chapter_id, qtype, difficulty, content, options, answer, analysis, score)
# --------------------------------------------------------------------------
QUESTIONS = [
    # ========== 第 1 章 函数与极限 ==========
    (1, "single", 1, r"求极限 \(\lim_{x\to 0}\dfrac{\sin x}{x}\) 的值。",
     ["0", "1", r"\(+\infty\)", "不存在"], "B", "重要极限之一，结果为 1。", 5),
    (1, "single", 2, r"求极限 \(\lim_{x\to\infty}\left(1+\dfrac{1}{x}\right)^x\) 的值。",
     ["1", r"\(e\)", "0", r"\(+\infty\)"], "B", "重要极限之一，结果为 e。", 5),
    (1, "judge", 1, "有限个无穷小之和仍是无穷小。",
     None, "T", "无穷小的运算法则，结论正确。", 5),
    (1, "fill", 2, r"计算 \(\lim_{x\to 0}\dfrac{\sin 3x}{x}=\) ______。",
     None, "3", r"\(\lim_{x\to0}\frac{\sin 3x}{x}=\lim_{x\to0}3\cdot\frac{\sin 3x}{3x}=3\)。", 5),
    (1, "multi", 3, "关于无穷小，下列说法正确的是（多选）。",
     ["有限个无穷小之和是无穷小", "无穷小与有界函数的乘积是无穷小",
      "两个无穷小的商一定是无穷小", "常数 0 是无穷小"], "A,B,D",
     "无穷小之商不为零时其商可能是非无穷小，C 错误。", 5),
    (1, "single", 2, r"函数 \(f(x)=\dfrac{1}{\ln(x-1)}\) 的定义域是（　）。",
     [r"\((1,+\infty)\)", r"\((1,2)\cup(2,+\infty)\)", r"\((2,+\infty)\)", r"\([1,+\infty)\)"], "B",
     "需满足 x-1>0 且 ln(x-1)≠0，故 x>1 且 x≠2。", 5),
    (1, "single", 2, r"求极限 \(\lim_{x\to 0}\dfrac{1-\cos x}{x^{2}}\) 的值。",
     [r"\(\dfrac{1}{2}\)", "1", "0", r"\(+\infty\)"], "A",
     r"等价无穷小 \(1-\cos x\sim \dfrac{x^{2}}{2}\)，故极限为 1/2。", 5),
    (1, "judge", 2, r"若 \(\lim_{x\to x_0}f(x)\) 存在，则 \(f(x)\) 在 \(x_0\) 处必有定义。",
     None, "F", "极限存在只要求 x 趋近 x₀ 时的变化趋势，与 x₀ 处是否有定义无关。", 5),
    (1, "fill", 1, r"\(\lim_{x\to 0}\dfrac{\ln(1+x)}{x}=\) ______。",
     None, "1", r"等价无穷小 \(\ln(1+x)\sim x\)，极限为 1。", 5),

    # ========== 第 2 章 导数与微分 ==========
    (2, "single", 1, r"求 \(\dfrac{d}{dx}\left(x^3\right)\) 的值。",
     [r"\(3x^2\)", r"\(x^2\)", r"\(3x\)", r"\(3x^3\)"], "A", "幂函数求导公式 (x^n)'=nx^{n-1}。", 5),
    (2, "single", 2, r"设 \(y=\sin x\)，则 \(y''=\)（　）。",
     [r"\(\sin x\)", r"\(-\sin x\)", r"\(\cos x\)", r"\(-\cos x\)"], "B", "求导两次。", 5),
    (2, "judge", 1, "函数在某点可导，则它在该点一定连续。",
     None, "T", "可导必连续，连续不一定可导。", 5),
    (2, "fill", 2, r"设 \(y=e^{2x}\)，则 \(dy=\) ______ \(dx\)。",
     None, r"2e^{2x}", "复合函数求导得 y'=2e^{2x}。", 5),
    (2, "single", 2, r"曲线 \(y=x^2\) 在点 \((1,1)\) 处切线的斜率为（　）。",
     ["1", "2", "0", "3"], "B", "y'=2x，代入 x=1 得 2。", 5),
    (2, "multi", 3, "关于导数，下列说法正确的是（多选）。",
     ["可导必连续", "连续必可导", "可导函数在可导点处有切线", "导数为 0 的点一定是极值点"],
     "A,C", "连续不一定可导（如 y=|x| 在 x=0），导数为 0 的点不一定是极值点，B、D 错误。", 5),
    (2, "single", 2, r"设 \(y=x^{2}e^{x}\)，则 \(y'=\)（　）。",
     [r"\(2xe^{x}\)", r"\(xe^{x}(2+x)\)", r"\(x^{2}e^{x}\)", r"\(e^{x}(x^{2}+2x+1)\)"], "B",
     "乘积法则：y'=2xe^x+x²e^x=xe^x(2+x)。", 5),
    (2, "fill", 2, r"设 \(y=\ln(3x+2)\)，则 \(y'=\) ______。",
     None, r"3/(3x+2)", "链式法则：外层 1/(3x+2) 乘内层导数 3。", 5),
    (2, "judge", 2, r"函数 \(y=|x|\) 在 \(x=0\) 处不可导。",
     None, "T", "左右导数分别为 -1 和 1，不相等，故不可导。", 5),

    # ========== 第 3 章 中值定理与导数应用 ==========
    (3, "single", 2, r"函数 \(f(x)=x^3-3x\) 的极大值点为（　）。",
     [r"\(x=1\)", r"\(x=-1\)", r"\(x=0\)", r"\(x=\pm1\)"], "A",
     "f'(x)=3x^2-3，令其为 0 得 x=±1；f''(1)=-6<0，故 x=1 为极大值点。", 5),
    (3, "judge", 2, "洛必达法则可用于求 0/0 型和 ∞/∞ 型不定式的极限。",
     None, "T", "洛必达法则的适用条件。", 5),
    (3, "fill", 2, r"计算 \(\lim_{x\to 0}\dfrac{e^x-1}{x}=\) ______。",
     None, "1", "0/0 型，用洛必达法则或等价无穷小 e^x-1~x，结果为 1。", 5),
    (3, "single", 3, r"函数 \(y=x-\ln x\) 的单调递减区间是（　）。",
     ["(0,1)", r"\((1,+\infty)\)", r"\((0,+\infty)\)", r"\((-\infty,1)\)"], "A",
     "y'=1-1/x，当 0<x<1 时 y'<0，函数递减。", 5),
    (3, "single", 2, r"拉格朗日中值定理的结论是（　）。",
     [r"\(f(b)-f(a)=f'(\xi)(b-a)\)", r"\(f'(\xi)=0\)",
      r"\(f(b)-f(a)=f'(\xi)\)", r"\(f'(\xi)=\dfrac{f(b)-f(a)}{2}\)"], "A",
     "拉格朗日中值定理的标准结论。", 5),
    (3, "fill", 3, r"计算 \(\lim_{x\to\infty}\dfrac{\ln x}{x}=\) ______。",
     None, "0", "∞/∞ 型，洛必达法则得 lim(1/x)/1=0。", 5),
    (3, "multi", 3, "关于函数极值，下列说法正确的是（多选）。",
     ["极值点处导数一定为 0", "极值点可能在不可导点处取得", "f'(x₀)=0 时 x₀ 一定是极值点", "f''(x₀)<0 且 f'(x₀)=0 时 x₀ 为极大值点"],
     "B,D", "极值点可能出现在不可导点（如 y=|x| 的 x=0），A 错；f'(x₀)=0 只是驻点，未必是极值点（如 y=x³），C 错。", 5),
    (3, "judge", 1, r"若 \(f''(x)>0\)，则曲线 \(y=f(x)\) 是凹的。",
     None, "T", "二阶导数大于零表示曲线凹（下凸）。", 5),

    # ========== 第 4 章 不定积分 ==========
    (4, "single", 1, r"计算 \(\int x\,dx\)。",
     [r"\(x^2+C\)", r"\(\dfrac{x^2}{2}+C\)", r"\(2x+C\)", r"\(\dfrac{x^2}{2}\)"], "B",
     "幂函数积分公式。", 5),
    (4, "fill", 2, r"计算 \(\int e^x\,dx=\) ______。",
     None, r"e^x+C", "基本积分公式。", 5),
    (4, "judge", 1, r"\(\int f(x)dx\) 表示 \(f(x)\) 的全体原函数。",
     None, "T", "不定积分的定义。", 5),
    (4, "single", 2, r"计算 \(\int \dfrac{1}{x}\,dx\)。",
     [r"\(\ln|x|+C\)", r"\(\dfrac{1}{x^2}+C\)", r"\(-\dfrac{1}{x^2}+C\)", r"\(x+C\)"], "A",
     "常用积分公式。", 5),
    (4, "single", 2, r"计算 \(\int 2x\cos(x^{2})\,dx\)。",
     [r"\(\sin(x^{2})+C\)", r"\(-\sin(x^{2})+C\)", r"\(2\sin(x^{2})+C\)", r"\(\cos(x^{2})+C\)"], "A",
     "凑微分：2xdx=d(x²)，令 u=x² 得 ∫cos u du=sin u+C。", 5),
    (4, "single", 3, r"计算 \(\int x e^{x}\,dx\)。",
     [r"\(xe^{x}-e^{x}+C\)", r"\(xe^{x}+e^{x}+C\)", r"\(\dfrac{x^{2}}{2}e^{x}+C\)", r"\(e^{x}(x+1)+C\)"], "A",
     "分部积分：u=x，dv=e^x dx，得 xe^x-∫e^x dx。", 5),
    (4, "judge", 2, r"\(\int \dfrac{2x}{1+x^{2}}dx=\ln(1+x^{2})+C\)。",
     None, "T", "凑微分 d(1+x²)=2xdx，积分为 ln(1+x²)+C。", 5),
    (4, "fill", 2, r"计算 \(\int \dfrac{dx}{1+x^{2}}=\) ______。",
     None, r"arctan x+C", "基本积分公式，结果为反正切函数。", 5),
    (4, "multi", 3, "下列积分结果正确的是（多选）。",
     [r"\(\int \sin x\,dx=-\cos x+C\)", r"\(\int \cos x\,dx=\sin x+C\)",
      r"\(\int a^{x}dx=\dfrac{a^{x}}{\ln a}+C\ (a>0,a\ne1)\)", r"\(\int x^{-1}dx=\dfrac{x^{0}}{0}+C\)"],
     "A,B,C", "∫x⁻¹dx=ln|x|+C，不能套用幂函数公式（α=-1 时公式失效），D 错。", 5),

    # ========== 第 5 章 定积分及其应用 ==========
    (5, "single", 1, r"计算定积分 \(\int_{0}^{1} x\,dx\)。",
     ["1", r"\(\dfrac{1}{2}\)", "0", "2"], "B",
     "牛顿-莱布尼茨公式，原函数为 x^2/2。", 5),
    (5, "judge", 2, r"若 \(f(x)\) 为奇函数，则 \(\int_{-a}^{a} f(x)dx=0\)。",
     None, "T", "奇函数在对称区间上的积分为 0。", 5),
    (5, "fill", 3, r"计算 \(\dfrac{d}{dx}\int_{0}^{x}\sin t\,dt=\) ______。",
     None, "sin x", "变限积分求导，结果为被积函数在 x 处的值 sin x。", 5),
    (5, "single", 2, r"计算定积分 \(\int_{0}^{\pi}\sin x\,dx\)。",
     ["0", "1", "2", "-2"], "C", "原函数 -cos x，代入得 1-(-1)=2。", 5),
    (5, "single", 2, r"计算定积分 \(\int_{1}^{e}\dfrac{1}{x}dx\)。",
     ["1", r"\(e\)", r"\(e-1\)", r"\(\dfrac{1}{2}\)"], "A", "[ln|x|]₁ᵉ=ln e-ln 1=1。", 5),
    (5, "fill", 2, r"由 \(y=x^{2}\) 与 \(y=x\) 所围图形的面积为 ______。",
     None, r"1/6", "S=∫₀¹(x-x²)dx=1/2-1/3=1/6。", 5),
    (5, "judge", 1, r"\(\int_{a}^{b}f(x)dx=-\int_{b}^{a}f(x)dx\)。",
     None, "T", "定积分的性质：交换上下限变号。", 5),
    (5, "single", 3, r"由 \(y=f(x)\) 绕 \(x\) 轴旋转所得旋转体体积为（　）。",
     [r"\(V=\pi\int_{a}^{b}f(x)dx\)", r"\(V=\pi\int_{a}^{b}f^{2}(x)dx\)",
      r"\(V=2\pi\int_{a}^{b}f(x)dx\)", r"\(V=\int_{a}^{b}f^{2}(x)dx\)"], "B",
     "圆盘法：体积微元 dV=πf²(x)dx。", 5),
    (5, "multi", 3, "关于微积分基本定理，下列说法正确的是（多选）。",
     ["把定积分计算转化为求原函数", "要求被积函数在区间上连续",
      "适用于任何可积函数", "连接了微分学与积分学"],
     "A,B,D", "微积分基本定理要求被积函数连续（更一般地可积但需原函数存在），C 表述过于宽泛。", 5),

    # ========== 第 6 章 常微分方程 ==========
    (6, "single", 1, r"微分方程 \(y'=y\) 的通解是（　）。",
     [r"\(y=Cx\)", r"\(y=Ce^{x}\)", r"\(y=\dfrac{C}{x}\)", r"\(y=x+C\)"], "B",
     "可分离变量方程，解得 y=Ce^x。", 5),
    (6, "judge", 2, r"方程 \(y'+y=0\) 是一阶线性微分方程。",
     None, "T", "符合一阶线性方程 y'+P(x)y=Q(x) 的形式。", 5),
    (6, "fill", 2, r"微分方程 \(y'=2x\) 的通解为 \(y=\) ______。",
     None, r"x^2+C", "两边积分得 y=x^2+C。", 5),
    (6, "single", 2, r"微分方程 \(y''-3y'+2y=0\) 的特征根是（　）。",
     [r"\(r_1=1,r_2=2\)", r"\(r_1=-1,r_2=-2\)", r"\(r_1=r_2=1\)", r"\(r=\pm i\)"], "A",
     "特征方程 r²-3r+2=(r-1)(r-2)=0。", 5),
    (6, "single", 2, r"微分方程 \(y''+y=0\) 的通解是（　）。",
     [r"\(C_1e^{x}+C_2e^{-x}\)", r"\(C_1\cos x+C_2\sin x\)", r"\((C_1+C_2x)e^{x}\)", r"\(C_1e^{ix}\)"], "B",
     "特征根为共轭复根 ±i，对应解为三角函数组合。", 5),
    (6, "fill", 3, r"方程 \(y'+y=e^{x}\) 的通解为 \(y=\) ______。",
     None, r"0.5e^x+Ce^{-x}", "积分因子 e^x 法：y=½e^x+Ce⁻ˣ。", 5),
    (6, "judge", 1, r"含一个任意常数的解一定是微分方程的通解。",
     None, "F", "通解所含独立任意常数的个数应等于方程的阶数。", 5),
]
