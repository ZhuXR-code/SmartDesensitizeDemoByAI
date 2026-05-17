一、颜色融合策略分析
1️⃣ 颜色光谱分布（已排序）
色系
	
色名
	
HEX
	
明度
	
冷暖
	
角色定位


新增柔色​
	
Lavender
	
#DED9E2
	
⬆️ 最亮
	
冷紫
	
高光 / 浅背景​


新增柔色​
	
Periwinkle
	
#C089DD
	
⬆️ 亮
	
冷暖交界
	
次级强调 / 渐变​


新增柔色​
	
Wisteria Blue
	
#80A1D4
	
⬆️ 中亮
	
冷蓝
	
信息色 / 链接​


原有主色​
	
Lime Cream
	
#F4FDAF
	
⬆️ 最亮
	
暖黄
	
核心强调 / CTA​


原有主色​
	
Light Gold
	
#EFDD8D
	
⬆️ 亮
	
暖黄
	
浅色表面​


原有主色​
	
Fern
	
#65743A
	
⬇️ 中
	
冷绿
	
自然 / 边框​


原有主色​
	
Dark Slate Grey
	
#394F49
	
⬇️ 暗
	
冷灰绿
	
深色表面​


新增深紫​
	
#6667AB
	
⬇️ 中暗
	
冷紫
	
主色过渡 / 图表​


新增深紫​
	
#7B337E
	
⬇️ 暗
	
冷紫
	
深紫强调 / 标签​


新增深紫​
	
#420D4B
	
⬇️ 更暗
	
冷紫
	
深色背景层​


新增深紫​
	
#210635
	
⬇️ 最暗
	
冷紫
	
页面基底​


原有深紫​
	
Midnight Violet
	
#210124
	
⬇️ 最暗
	
冷紫
	
页面基底（保留）​
2️⃣ 融合后的设计逻辑
✅ 不再只有“黑夜”​
✅ 引入 “暮色 + 柔光”​ 的层次感
✅ 解决原方案“对比过强、略显沉闷”的问题
新的视觉叙事：
深夜（Midnight Violet） → 紫雾（Wisteria / Periwinkle） → 萤火（Lime Cream）
二、融合后的最终色彩系统（Final Color System）
⚠️ AI 生成代码时必须严格使用此表
2.1 背景层（Backgrounds）
角色
	
色值
	
说明


Base​
	
#210124/ #210635
	
页面最底层（保留原色，极深紫）


Surface Dark​
	
#420D4B
	
深色卡片、侧边栏


Surface Soft​
	
#6667AB
	
次级区域、图表背景


Glass Base​
	
rgba(33, 6, 53, 0.7)
	
毛玻璃基底
2.2 前景层（Foreground / Content）
角色
	
色值
	
说明


Primary Text​
	
#F4FDAF
	
主标题、主按钮文字（保留）


Secondary Text​
	
#EFDD8D
	
正文、说明文字（保留）


Tertiary Text​
	
#DED9E2(Lavender)
	
辅助文字、占位符


Accent Warm​
	
#F5D5E0
	
强调文字、标签背景


Accent Cool​
	
#80A1D4(Wisteria)
	
链接、信息提示
2.3 功能色（Functional Colors）
类型
	
色值
	
说明


Success​
	
#65743A(Fern)
	
成功状态（保留）


Info​
	
#80A1D4(Wisteria)
	
信息提示


Warning​
	
#EFDD8D(Light Gold)
	
警告


Danger / Error​
	
#7B337E
	
错误、删除、高危操作


Border​
	
rgba(222, 217, 226, 0.2)
	
边框（使用 Lavender 透明）
2.4 渐变推荐（Gradients）
// 主渐变（按钮 / Banner）
$gradient-primary: linear-gradient(135deg, #F4FDAF 0%, #EFDD8D 100%);

// 柔光渐变（卡片背景 / Hover）
$gradient-soft: linear-gradient(135deg, rgba(192, 137, 221, 0.2) 0%, rgba(128, 161, 212, 0.2) 100%);

// 深紫渐变（导航栏 / Footer）
$gradient-dark: linear-gradient(180deg, #210124 0%, #420D4B 100%);
三、对现有组件的颜色适配建议
3.1 导航栏（Navbar）
背景：linear-gradient(180deg, #210124, #420D4B)
菜单文字：默认 #DED9E2，Hover 变为 #F4FDAF
激活指示器：#F4FDAF（保持不变，作为视觉锚点）
3.2 菜单卡片（Menu Card）
背景：rgba(102, 103, 171, 0.6)+ blur(20px)
边框：rgba(222, 217, 226, 0.2)
Hover 态：背景变亮 + 左侧 3px 竖线（颜色 #F4FDAF）
3.3 按钮（Button）
Primary：保留 #F4FDAF→ #210124文字
Secondary：背景透明，边框 #DED9E2，文字 #DED9E2
Ghost：无背景，文字 #80A1D4（Wisteria）
3.4 标签 / Badge
成功：#65743A
信息：#80A1D4
警告：#EFDD8D
错误：#7B337E