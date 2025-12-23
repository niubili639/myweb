<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref, watch, nextTick } from "vue";
import dayjs from "dayjs";
import duration from "dayjs/plugin/duration";
import {
  createCouple,
  fetchMyCouple,
  listCountdowns,
  addCountdown,
  updateCountdown,
  deleteCountdown,
  listWishes,
  addWish,
  updateWish,
  deleteWish,
  type Couple,
  type Countdown,
  type Wish,
} from "@/api/couples";
import { getApiKey } from "@/api/auth";
import { uploadImage } from "@/api/imageHost";
import { globalToast } from "@/composables/useToast";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
import { useRouter } from "vue-router";

dayjs.extend(duration);

const router = useRouter();
const confirmDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);

const couple = ref<Couple | null>(null);
const countdowns = ref<Countdown[]>([]);
const wishes = ref<Wish[]>([]);
let timer: number | undefined;
const heartbeat = ref(0);

// 表单
const coupleForm = ref({
  name: "我们的故事",
  partner_a_name: "",
  partner_b_name: "",
  partner_a_avatar: "",
  partner_b_avatar: "",
  partner_a_birthday: "",
  partner_b_birthday: "",
  partner_a_location: "",
  partner_b_location: "",
  start_date: dayjs().format("YYYY-MM-DD"),
});

// 弹窗状态
const showProfileModal = ref(false);
const showCountdownModal = ref(false);
const showWishModal = ref(false);

// 新增表单
const newCountdown = ref({ title: "", target_date: "", is_yearly: false });
const newWish = ref({ title: "" });

// 头像上传
const avatarUploading = ref<"a" | "b" | null>(null);
const avatarInputA = ref<HTMLInputElement | null>(null);
const avatarInputB = ref<HTMLInputElement | null>(null);

// 地图相关
const amapKey = ref("");
const amapSafeKey = ref("");
const mapContainer = ref<HTMLDivElement | null>(null);
let mapInstance: any = null;
const locationA = ref({ lng: 0, lat: 0, name: "" });
const locationB = ref({ lng: 0, lat: 0, name: "" });
const distance = ref<number | null>(null);
const mapLoading = ref(false);
const mapError = ref("");

const elapsed = computed(() => {
  heartbeat.value;
  if (!couple.value?.start_date) return { d: 0, h: 0, m: 0, s: 0 };
  const diff = dayjs.duration(dayjs().diff(dayjs(couple.value.start_date)));
  return { d: Math.floor(diff.asDays()), h: diff.hours(), m: diff.minutes(), s: diff.seconds() };
});

// 计算倒计时（精确到秒）
const getCountdownTime = (targetDate: string, isYearly: boolean) => {
  heartbeat.value;
  let target = dayjs(targetDate);
  if (isYearly) {
    target = target.year(dayjs().year());
    if (target.isBefore(dayjs(), "day")) {
      target = target.add(1, "year");
    }
  }
  const diff = dayjs.duration(target.diff(dayjs()));
  if (diff.asMilliseconds() <= 0) return { d: 0, h: 0, m: 0, s: 0, passed: true };
  return { d: Math.floor(diff.asDays()), h: diff.hours(), m: diff.minutes(), s: diff.seconds(), passed: false };
};

// 编辑状态
const editingCountdown = ref<number | null>(null);
const editingCountdownDate = ref<number | null>(null);
const editingWish = ref<number | null>(null);
const editCountdownTitle = ref("");
const editCountdownDate = ref("");
const editWishTitle = ref("");

// 加载高德地图 SDK
const loadAmapSDK = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    if ((window as any).AMap) {
      console.log("[AMap] SDK 已加载");
      resolve();
      return;
    }
    console.log("[AMap] 开始加载 SDK, key:", amapKey.value, "safeKey:", amapSafeKey.value ? "已设置" : "未设置");
    
    // 高德 2.0 需要配置安全密钥
    (window as any)._AMapSecurityConfig = {
      securityJsCode: amapSafeKey.value,
    };
    
    const script = document.createElement("script");
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${amapKey.value}&plugin=AMap.Geocoder`;
    script.onload = () => {
      console.log("[AMap] SDK 加载成功");
      resolve();
    };
    script.onerror = (e) => {
      console.error("[AMap] SDK 加载失败", e);
      reject(new Error("加载高德地图失败"));
    };
    document.head.appendChild(script);
  });
};

// 地理编码：城市名 -> 经纬度
const geocode = async (address: string): Promise<{ lng: number; lat: number } | null> => {
  const AMap = (window as any).AMap;
  return new Promise((resolve) => {
    console.log("[AMap Geocode] 开始解析:", address);
    const geocoder = new AMap.Geocoder({ city: "全国" });
    geocoder.getLocation(address, (status: string, result: any) => {
      console.log("[AMap Geocode]", address, "=>", status, result);
      if (status === "complete" && result.geocodes?.length) {
        const { lng, lat } = result.geocodes[0].location;
        resolve({ lng, lat });
      } else {
        console.warn("[AMap Geocode] 失败:", status, result);
        resolve(null);
      }
    });
    // 添加超时处理
    setTimeout(() => {
      console.warn("[AMap Geocode] 超时:", address);
      resolve(null);
    }, 10000);
  });
};

// 计算两点距离（公里）
const calcDistance = (p1: { lng: number; lat: number }, p2: { lng: number; lat: number }) => {
  const AMap = (window as any).AMap;
  const lnglat1 = new AMap.LngLat(p1.lng, p1.lat);
  const lnglat2 = new AMap.LngLat(p2.lng, p2.lat);
  return Math.round(lnglat1.distance(lnglat2) / 1000);
};

// 初始化地图
const initMap = async () => {
  if (!amapKey.value || !mapContainer.value) {
    console.log("[AMap] 跳过初始化: key=", amapKey.value, "container=", !!mapContainer.value);
    return;
  }
  mapLoading.value = true;
  mapError.value = "";
  console.log("[AMap] 开始初始化地图");
  try {
    await loadAmapSDK();
    const AMap = (window as any).AMap;
    
    // 获取两个位置的坐标
    const addrA = coupleForm.value.partner_a_location;
    const addrB = coupleForm.value.partner_b_location;
    console.log("[AMap] 位置:", addrA, addrB);
    
    if (addrA) {
      const pos = await geocode(addrA);
      if (pos) {
        locationA.value = { ...pos, name: addrA };
      }
    }
    if (addrB) {
      const pos = await geocode(addrB);
      if (pos) {
        locationB.value = { ...pos, name: addrB };
      }
    }

    console.log("[AMap] 解析结果:", locationA.value, locationB.value);

    // 计算中心点和距离
    let center = [116.397428, 39.90923]; // 默认北京
    if (locationA.value.lng && locationB.value.lng) {
      center = [(locationA.value.lng + locationB.value.lng) / 2, (locationA.value.lat + locationB.value.lat) / 2];
      distance.value = calcDistance(locationA.value, locationB.value);
    } else if (locationA.value.lng) {
      center = [locationA.value.lng, locationA.value.lat];
    } else if (locationB.value.lng) {
      center = [locationB.value.lng, locationB.value.lat];
    }

    // 创建地图
    if (mapInstance) {
      mapInstance.destroy();
    }
    mapInstance = new AMap.Map(mapContainer.value, {
      zoom: locationA.value.lng && locationB.value.lng ? 5 : 10,
      center,
      mapStyle: "amap://styles/macaron", // 马卡龙风格，粉色系
    });

    // 添加标记
    if (locationA.value.lng) {
      new AMap.Marker({
        position: [locationA.value.lng, locationA.value.lat],
        map: mapInstance,
        label: { content: `<div class="map-label">${coupleForm.value.partner_a_name || 'TA'}</div>`, direction: "top" },
      });
    }
    if (locationB.value.lng) {
      new AMap.Marker({
        position: [locationB.value.lng, locationB.value.lat],
        map: mapInstance,
        label: { content: `<div class="map-label">${coupleForm.value.partner_b_name || '我'}</div>`, direction: "top" },
      });
    }

    // 画连线
    if (locationA.value.lng && locationB.value.lng) {
      new AMap.Polyline({
        path: [[locationA.value.lng, locationA.value.lat], [locationB.value.lng, locationB.value.lat]],
        strokeColor: "#ff6b9d",
        strokeWeight: 2,
        strokeStyle: "dashed",
        map: mapInstance,
      });
      mapInstance.setFitView();
    }
    console.log("[AMap] 地图初始化完成");
  } catch (err) {
    console.error("[AMap] 初始化失败:", err);
    mapError.value = (err as Error).message;
  } finally {
    mapLoading.value = false;
  }
};

// 加载数据
const loadData = async () => {
  try {
    // 加载高德 Key（必须在 SDK 加载前设置安全密钥）
    try {
      const keyData = await getApiKey("amap_web_key");
      amapKey.value = keyData.key;
    } catch { /* ignore */ }
    try {
      const safeKeyData = await getApiKey("amap_web_safe_key");
      amapSafeKey.value = safeKeyData.key;
      // 立即设置安全密钥，确保在任何 AMap 调用前生效
      (window as any)._AMapSecurityConfig = {
        securityJsCode: safeKeyData.key,
      };
      console.log("[AMap] 安全密钥已设置");
    } catch { /* ignore */ }

    const data = await fetchMyCouple();
    couple.value = data;
    if (data) {
      coupleForm.value = {
        name: data.name || "我们的故事",
        partner_a_name: data.partner_a_name || "",
        partner_b_name: data.partner_b_name || "",
        partner_a_avatar: data.partner_a_avatar || "",
        partner_b_avatar: data.partner_b_avatar || "",
        partner_a_birthday: data.partner_a_birthday || "",
        partner_b_birthday: data.partner_b_birthday || "",
        partner_a_location: data.partner_a_location || "",
        partner_b_location: data.partner_b_location || "",
        start_date: data.start_date || dayjs().format("YYYY-MM-DD"),
      };
      countdowns.value = await listCountdowns(data.id);
      wishes.value = await listWishes(data.id);
      
      // 初始化地图
      await nextTick();
      if (amapKey.value) {
        initMap();
      }
    }
  } catch (err) {
    globalToast.error((err as Error).message);
  }
};

// 保存档案
const saveProfile = async () => {
  try {
    couple.value = await createCouple(coupleForm.value);
    showProfileModal.value = false;
    globalToast.success("保存成功");
    await loadData();
  } catch (err) {
    globalToast.error((err as Error).message);
  }
};

// 上传头像
const handleAvatarUpload = async (e: Event, partner: "a" | "b") => {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  avatarUploading.value = partner;
  try {
    const res = await uploadImage(file);
    if (res.status && res.data) {
      if (partner === "a") {
        coupleForm.value.partner_a_avatar = res.data.links.url;
      } else {
        coupleForm.value.partner_b_avatar = res.data.links.url;
      }
      globalToast.success("头像上传成功");
    }
  } catch (err) {
    globalToast.error("上传失败");
  } finally {
    avatarUploading.value = null;
  }
};

// 倒计时操作
const submitCountdown = async () => {
  if (!couple.value || !newCountdown.value.title || !newCountdown.value.target_date) return;
  try {
    await addCountdown(couple.value.id, newCountdown.value);
    countdowns.value = await listCountdowns(couple.value.id);
    newCountdown.value = { title: "", target_date: "", is_yearly: false };
    showCountdownModal.value = false;
    globalToast.success("添加成功");
  } catch (err) {
    globalToast.error((err as Error).message);
  }
};

const removeCountdown = async (id: number) => {
  const confirmed = await confirmDialog.value?.show({ title: "删除倒计时", message: "确定要删除吗？", type: "danger" });
  if (!confirmed || !couple.value) return;
  try {
    await deleteCountdown(couple.value.id, id);
    countdowns.value = await listCountdowns(couple.value.id);
    globalToast.success("已删除");
  } catch (err) {
    globalToast.error((err as Error).message);
  }
};

const startEditCountdown = (cd: Countdown) => { editingCountdown.value = cd.id; editCountdownTitle.value = cd.title; };
const saveCountdownTitle = async (cd: Countdown) => {
  if (!couple.value || !editCountdownTitle.value.trim()) { editingCountdown.value = null; return; }
  try {
    await updateCountdown(couple.value.id, cd.id, { title: editCountdownTitle.value.trim() });
    countdowns.value = await listCountdowns(couple.value.id);
    globalToast.success("已更新");
  } catch (err) { globalToast.error((err as Error).message); }
  editingCountdown.value = null;
};

const startEditCountdownDate = (cd: Countdown) => { editingCountdownDate.value = cd.id; editCountdownDate.value = cd.target_date; };
const saveCountdownDate = async (cd: Countdown) => {
  if (!couple.value || !editCountdownDate.value) { editingCountdownDate.value = null; return; }
  try {
    await updateCountdown(couple.value.id, cd.id, { target_date: editCountdownDate.value });
    countdowns.value = await listCountdowns(couple.value.id);
    globalToast.success("已更新");
  } catch (err) { globalToast.error((err as Error).message); }
  editingCountdownDate.value = null;
};

const togglePinCountdown = async (cd: Countdown) => {
  if (!couple.value) return;
  try {
    await updateCountdown(couple.value.id, cd.id, { is_pinned: !cd.is_pinned });
    countdowns.value = await listCountdowns(couple.value.id);
    globalToast.success(cd.is_pinned ? "已取消置顶" : "已置顶");
  } catch (err) { globalToast.error((err as Error).message); }
};

const startEditWish = (wish: Wish) => { editingWish.value = wish.id; editWishTitle.value = wish.title; };
const saveWishTitle = async (wish: Wish) => {
  if (!couple.value || !editWishTitle.value.trim()) { editingWish.value = null; return; }
  try {
    await updateWish(couple.value.id, wish.id, { title: editWishTitle.value.trim() });
    wishes.value = await listWishes(couple.value.id);
    globalToast.success("已更新");
  } catch (err) { globalToast.error((err as Error).message); }
  editingWish.value = null;
};

const submitWish = async () => {
  if (!couple.value || !newWish.value.title) return;
  try {
    await addWish(couple.value.id, newWish.value);
    wishes.value = await listWishes(couple.value.id);
    newWish.value = { title: "" };
    showWishModal.value = false;
    globalToast.success("添加成功");
  } catch (err) { globalToast.error((err as Error).message); }
};

const toggleWish = async (wish: Wish) => {
  if (!couple.value) return;
  try {
    await updateWish(couple.value.id, wish.id, { completed: !wish.completed, progress: wish.completed ? 0 : 100 });
    wishes.value = await listWishes(couple.value.id);
  } catch (err) { globalToast.error((err as Error).message); }
};

const togglePinWish = async (wish: Wish) => {
  if (!couple.value) return;
  try {
    await updateWish(couple.value.id, wish.id, { is_pinned: !wish.is_pinned });
    wishes.value = await listWishes(couple.value.id);
    globalToast.success(wish.is_pinned ? "已取消置顶" : "已置顶");
  } catch (err) { globalToast.error((err as Error).message); }
};

const removeWish = async (id: number) => {
  const confirmed = await confirmDialog.value?.show({ title: "删除愿望", message: "确定要删除吗？", type: "danger" });
  if (!confirmed || !couple.value) return;
  try {
    await deleteWish(couple.value.id, id);
    wishes.value = await listWishes(couple.value.id);
    globalToast.success("已删除");
  } catch (err) { globalToast.error((err as Error).message); }
};

// 骰子游戏
const diceA = ref(1);
const diceB = ref(1);
const diceRolling = ref(false);
const diceWinner = ref<string | null>(null);

const rollDice = () => {
  if (diceRolling.value) return;
  diceRolling.value = true;
  diceWinner.value = null;
  
  // 动画效果：快速切换数字
  let count = 0;
  const interval = setInterval(() => {
    diceA.value = Math.floor(Math.random() * 6) + 1;
    diceB.value = Math.floor(Math.random() * 6) + 1;
    count++;
    if (count >= 15) {
      clearInterval(interval);
      // 最终结果
      diceA.value = Math.floor(Math.random() * 6) + 1;
      diceB.value = Math.floor(Math.random() * 6) + 1;
      diceRolling.value = false;
      // 判断胜负
      const nameA = coupleForm.value.partner_a_name || "TA";
      const nameB = coupleForm.value.partner_b_name || "我";
      if (diceA.value > diceB.value) {
        diceWinner.value = `${nameA} 赢了！🎉`;
      } else if (diceB.value > diceA.value) {
        diceWinner.value = `${nameB} 赢了！🎉`;
      } else {
        diceWinner.value = "平局！再来一次？";
      }
    }
  }, 80);
};

const diceEmoji = (n: number) => ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"][n - 1];

onMounted(() => {
  loadData();
  timer = window.setInterval(() => { heartbeat.value += 1; }, 1000);
});

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer);
  if (mapInstance) mapInstance.destroy();
});
</script>

<template>
  <div class="page">
    <ConfirmDialog ref="confirmDialog" />

    <!-- 顶部卡片 -->
    <section class="hero-section">
      <div class="hero-card">
        <div class="couple-avatars">
          <div class="avatar-item">
            <div class="avatar" :style="coupleForm.partner_a_avatar ? { backgroundImage: `url(${coupleForm.partner_a_avatar})` } : {}">
              {{ coupleForm.partner_a_avatar ? '' : '👤' }}
            </div>
            <span class="name">{{ coupleForm.partner_a_name || 'TA' }}</span>
          </div>
          <div class="heart-icon">❤️</div>
          <div class="avatar-item">
            <div class="avatar" :style="coupleForm.partner_b_avatar ? { backgroundImage: `url(${coupleForm.partner_b_avatar})` } : {}">
              {{ coupleForm.partner_b_avatar ? '' : '👤' }}
            </div>
            <span class="name">{{ coupleForm.partner_b_name || '我' }}</span>
          </div>
        </div>
        <p class="together-text">我们已经在一起</p>
        <div class="time-display">
          <div class="time-item"><span class="num">{{ elapsed.d }}</span><span class="unit">天</span></div>
          <div class="time-item"><span class="num">{{ elapsed.h }}</span><span class="unit">时</span></div>
          <div class="time-item"><span class="num">{{ elapsed.m }}</span><span class="unit">分</span></div>
          <div class="time-item"><span class="num">{{ elapsed.s }}</span><span class="unit">秒</span></div>
        </div>
      </div>
    </section>

    <!-- 快捷入口 -->
    <section class="quick-section">
      <div class="quick-grid">
        <div class="quick-card" @click="router.push('/notes/couple')">
          <span class="quick-icon">📘</span>
          <div><p class="quick-title">点点滴滴</p><p class="quick-desc">记录生活</p></div>
        </div>
        <div class="quick-card" @click="router.push('/messages')">
          <span class="quick-icon">💌</span>
          <div><p class="quick-title">留言板</p><p class="quick-desc">写下祝福</p></div>
        </div>
        <div class="quick-card" @click="router.push('/album/couple')">
          <span class="quick-icon">📸</span>
          <div><p class="quick-title">相册</p><p class="quick-desc">美好回忆</p></div>
        </div>
      </div>
    </section>

    <!-- 倒计时 -->
    <section class="main-content">
      <div class="left-column">
        <!-- 倒计时 -->
        <div class="card-section">
          <div class="section-header">
            <h3>📅 纪念日倒计时</h3>
            <button class="add-btn" @click="showCountdownModal = true">+ 添加</button>
          </div>
          <div v-if="countdowns.length" class="countdown-list scrollable">
            <div v-for="cd in countdowns" :key="cd.id" :class="['countdown-item', { pinned: cd.is_pinned }]">
              <div class="countdown-info">
                <input v-if="editingCountdown === cd.id" v-model="editCountdownTitle" class="edit-input" @blur="saveCountdownTitle(cd)" @keyup.enter="saveCountdownTitle(cd)" @keyup.esc="editingCountdown = null" autofocus />
                <span v-else class="countdown-title editable" @click="startEditCountdown(cd)">
                  <span v-if="cd.is_pinned" class="pin-icon">📌</span>{{ cd.title }}
                </span>
                <input v-if="editingCountdownDate === cd.id" v-model="editCountdownDate" type="date" class="edit-input date-input" @blur="saveCountdownDate(cd)" @change="saveCountdownDate(cd)" @keyup.esc="editingCountdownDate = null" autofocus />
                <span v-else class="countdown-date editable" @click="startEditCountdownDate(cd)">{{ cd.target_date }}</span>
              </div>
              <div class="countdown-time">
                <template v-if="getCountdownTime(cd.target_date, cd.is_yearly).passed"><span class="time-passed">🎉 已到达</span></template>
                <template v-else>
                  <span class="time-num">{{ getCountdownTime(cd.target_date, cd.is_yearly).d }}</span><span class="time-unit">天</span>
                  <span class="time-num">{{ getCountdownTime(cd.target_date, cd.is_yearly).h }}</span><span class="time-unit">时</span>
                  <span class="time-num">{{ getCountdownTime(cd.target_date, cd.is_yearly).m }}</span><span class="time-unit">分</span>
                  <span class="time-num">{{ getCountdownTime(cd.target_date, cd.is_yearly).s }}</span><span class="time-unit">秒</span>
                </template>
              </div>
              <div class="item-actions">
                <button class="action-btn pin-btn" @click="togglePinCountdown(cd)" :title="cd.is_pinned ? '取消置顶' : '置顶'">{{ cd.is_pinned ? '📌' : '📍' }}</button>
                <button class="action-btn delete-btn" @click="removeCountdown(cd.id)">×</button>
              </div>
            </div>
          </div>
          <p v-else class="empty-hint">添加生日、纪念日等重要日期</p>
        </div>

        <!-- 愿望清单 -->
        <div class="card-section">
          <div class="section-header">
            <h3>✨ 愿望清单</h3>
            <button class="add-btn" @click="showWishModal = true">+ 添加</button>
          </div>
          <div v-if="wishes.length" class="wish-list scrollable">
            <div v-for="wish in wishes" :key="wish.id" :class="['wish-item', { completed: wish.completed, pinned: wish.is_pinned }]">
              <label class="wish-checkbox">
                <input type="checkbox" :checked="wish.completed" @change="toggleWish(wish)" />
                <input v-if="editingWish === wish.id" v-model="editWishTitle" class="edit-input" @blur="saveWishTitle(wish)" @keyup.enter="saveWishTitle(wish)" @keyup.esc="editingWish = null" autofocus />
                <span v-else class="wish-title editable" @click.stop="startEditWish(wish)">
                  <span v-if="wish.is_pinned" class="pin-icon">📌</span>{{ wish.title }}
                </span>
              </label>
              <div class="item-actions">
                <button class="action-btn pin-btn" @click="togglePinWish(wish)" :title="wish.is_pinned ? '取消置顶' : '置顶'">{{ wish.is_pinned ? '📌' : '📍' }}</button>
                <button class="action-btn delete-btn" @click="removeWish(wish.id)">×</button>
              </div>
            </div>
          </div>
          <p v-else class="empty-hint">添加你们想一起完成的事</p>
        </div>

        <!-- 双人小游戏 - 摇骰子 -->
        <div class="card-section game-section">
          <div class="section-header">
            <h3>🎲 摇骰子</h3>
          </div>
          <div class="dice-game">
            <div class="dice-players">
              <div class="dice-player">
                <span class="player-name">{{ coupleForm.partner_a_name || 'TA' }}</span>
                <span :class="['dice', { rolling: diceRolling }]">{{ diceEmoji(diceA) }}</span>
                <span class="dice-num">{{ diceA }} 点</span>
              </div>
              <span class="vs">VS</span>
              <div class="dice-player">
                <span class="player-name">{{ coupleForm.partner_b_name || '我' }}</span>
                <span :class="['dice', { rolling: diceRolling }]">{{ diceEmoji(diceB) }}</span>
                <span class="dice-num">{{ diceB }} 点</span>
              </div>
            </div>
            <p v-if="diceWinner" class="dice-result">{{ diceWinner }}</p>
            <button class="roll-btn" @click="rollDice" :disabled="diceRolling">
              {{ diceRolling ? '🎲 摇动中...' : '🎲 开始摇骰子' }}
            </button>
          </div>
        </div>
      </div>

      <div class="right-column">
        <!-- 地图 -->
        <div class="card-section map-section">
          <div v-if="!amapKey" class="map-placeholder">
            <span class="placeholder-icon">🗺️</span>
            <p>请在设置中配置高德地图 API Key</p>
          </div>
          <template v-else>
            <div class="distance-card">
              <div class="distance-header">
                <span class="distance-icon">📍</span>
                <span class="distance-title">我们的距离</span>
              </div>
              <div class="location-display">
                <div class="location-item">
                  <div class="location-avatar" :style="coupleForm.partner_a_avatar ? { backgroundImage: `url(${coupleForm.partner_a_avatar})` } : {}">
                    {{ coupleForm.partner_a_avatar ? '' : '👤' }}
                  </div>
                  <div class="location-info">
                    <span class="location-name">{{ coupleForm.partner_a_name || 'TA' }}</span>
                    <span class="location-addr">{{ coupleForm.partner_a_location || '未设置位置' }}</span>
                  </div>
                </div>
                <div class="distance-line">
                  <span class="line"></span>
                  <span v-if="distance !== null" class="distance-badge">{{ distance }} km</span>
                  <span v-else class="distance-badge">?</span>
                  <span class="line"></span>
                </div>
                <div class="location-item">
                  <div class="location-avatar" :style="coupleForm.partner_b_avatar ? { backgroundImage: `url(${coupleForm.partner_b_avatar})` } : {}">
                    {{ coupleForm.partner_b_avatar ? '' : '👤' }}
                  </div>
                  <div class="location-info">
                    <span class="location-name">{{ coupleForm.partner_b_name || '我' }}</span>
                    <span class="location-addr">{{ coupleForm.partner_b_location || '未设置位置' }}</span>
                  </div>
                </div>
              </div>
              <p v-if="distance !== null" class="distance-text">
                💕 相隔 <strong>{{ distance }}</strong> 公里，心却零距离
              </p>
            </div>
            <div ref="mapContainer" class="map-container">
              <div v-if="mapLoading" class="map-loading"><span class="spinner"></span></div>
              <div v-if="mapError" class="map-error">{{ mapError }}</div>
            </div>
          </template>
        </div>
      </div>
    </section>

    <!-- 修改档案按钮 -->
    <section class="edit-section">
      <button class="edit-btn" @click="showProfileModal = true">⚙️ 修改档案</button>
    </section>

    <!-- 修改档案弹窗 -->
    <Teleport to="body">
      <div v-if="showProfileModal" class="modal-overlay" @click.self="showProfileModal = false">
        <div class="modal profile-modal">
          <h3>修改档案</h3>
          <div class="form-grid">
            <div class="avatar-upload-group">
              <div class="avatar-upload" @click="avatarInputA?.click()">
                <div class="avatar-preview" :style="coupleForm.partner_a_avatar ? { backgroundImage: `url(${coupleForm.partner_a_avatar})` } : {}">
                  {{ avatarUploading === 'a' ? '...' : (coupleForm.partner_a_avatar ? '' : '📷') }}
                </div>
                <span>TA 的头像</span>
                <input ref="avatarInputA" type="file" accept="image/*" hidden @change="e => handleAvatarUpload(e, 'a')" />
              </div>
              <div class="avatar-upload" @click="avatarInputB?.click()">
                <div class="avatar-preview" :style="coupleForm.partner_b_avatar ? { backgroundImage: `url(${coupleForm.partner_b_avatar})` } : {}">
                  {{ avatarUploading === 'b' ? '...' : (coupleForm.partner_b_avatar ? '' : '📷') }}
                </div>
                <span>我的头像</span>
                <input ref="avatarInputB" type="file" accept="image/*" hidden @change="e => handleAvatarUpload(e, 'b')" />
              </div>
            </div>
            <label class="field"><span>TA 的昵称</span><input v-model="coupleForm.partner_a_name" placeholder="昵称" /></label>
            <label class="field"><span>我的昵称</span><input v-model="coupleForm.partner_b_name" placeholder="昵称" /></label>
            <label class="field"><span>TA 的生日</span><input v-model="coupleForm.partner_a_birthday" type="date" /></label>
            <label class="field"><span>我的生日</span><input v-model="coupleForm.partner_b_birthday" type="date" /></label>
            <label class="field"><span>TA 的位置</span><input v-model="coupleForm.partner_a_location" placeholder="如：浙江省杭州市西湖区" /></label>
            <label class="field"><span>我的位置</span><input v-model="coupleForm.partner_b_location" placeholder="如：江苏省南京市鼓楼区" /></label>
            <label class="field full"><span>在一起的日期</span><input v-model="coupleForm.start_date" type="date" /></label>
          </div>
          <div class="modal-actions">
            <button class="btn ghost" @click="showProfileModal = false">取消</button>
            <button class="btn primary" @click="saveProfile">保存</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 添加倒计时弹窗 -->
    <Teleport to="body">
      <div v-if="showCountdownModal" class="modal-overlay" @click.self="showCountdownModal = false">
        <div class="modal small-modal">
          <h3>添加倒计时</h3>
          <label class="field"><span>标题</span><input v-model="newCountdown.title" placeholder="如：恋爱纪念日" /></label>
          <label class="field"><span>日期</span><input v-model="newCountdown.target_date" type="date" /></label>
          <label class="checkbox-field">
            <input type="checkbox" v-model="newCountdown.is_yearly" />
            <span>每年重复（如生日）</span>
          </label>
          <div class="modal-actions">
            <button class="btn ghost" @click="showCountdownModal = false">取消</button>
            <button class="btn primary" @click="submitCountdown">添加</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 添加愿望弹窗 -->
    <Teleport to="body">
      <div v-if="showWishModal" class="modal-overlay" @click.self="showWishModal = false">
        <div class="modal small-modal">
          <h3>添加愿望</h3>
          <label class="field"><span>愿望内容</span><input v-model="newWish.title" placeholder="如：一起去旅行" /></label>
          <div class="modal-actions">
            <button class="btn ghost" @click="showWishModal = false">取消</button>
            <button class="btn primary" @click="submitWish">添加</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.page { padding: 0 0 60px; max-width: 1400px; margin: 0 auto; width: 90%; }

/* Hero */
.hero-section { 
  background: linear-gradient(135deg, #ffe9f1 0%, #fff6fb 50%, #ffeef5 100%);
  padding: 40px 20px;
  position: relative;
  overflow: hidden;
}
.hero-section::before {
  content: "💕";
  position: absolute;
  font-size: 120px;
  opacity: 0.08;
  top: -20px;
  left: 5%;
  animation: float 6s ease-in-out infinite;
}
.hero-section::after {
  content: "💗";
  position: absolute;
  font-size: 80px;
  opacity: 0.06;
  bottom: 10px;
  right: 8%;
  animation: float 8s ease-in-out infinite reverse;
}
@keyframes float {
  0%, 100% { transform: translateY(0) rotate(-5deg); }
  50% { transform: translateY(-15px) rotate(5deg); }
}
.hero-card { text-align: center; position: relative; z-index: 1; }
.couple-avatars { display: flex; align-items: center; justify-content: center; gap: 24px; margin-bottom: 20px; }
.avatar-item { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.avatar { width: 90px; height: 90px; border-radius: 50%; background: white; display: flex; align-items: center; justify-content: center; font-size: 36px; border: 4px solid white; box-shadow: 0 6px 20px rgba(235, 64, 120, 0.2); background-size: cover; background-position: center; }
.name { font-weight: 600; color: var(--text-main); font-size: 15px; }
.heart-icon { font-size: 32px; animation: pulse 1.5s ease infinite; }
@keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.2); } }
.together-text { color: #c21b68; margin: 0 0 12px; font-size: 15px; font-weight: 500; }
.time-display { display: flex; justify-content: center; align-items: baseline; gap: 8px; }
.time-item { display: flex; align-items: baseline; }
.num { font-size: 42px; font-weight: 800; color: #c21b68; }
.unit { font-size: 16px; color: #e85a9c; margin-left: 2px; margin-right: 12px; font-weight: 500; }

/* Quick */
.quick-section { padding: 20px; }
.quick-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.quick-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 16px; display: flex; align-items: center; gap: 12px; cursor: pointer; transition: all 0.2s; }
.quick-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(235, 64, 120, 0.12); }
.quick-icon { font-size: 28px; }
.quick-title { margin: 0; font-weight: 600; font-size: 15px; }
.quick-desc { margin: 2px 0 0; font-size: 12px; color: var(--text-muted); }

/* Main Content - 左右布局 */
.main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; padding: 0 20px 20px; }
.left-column, .right-column { display: flex; flex-direction: column; gap: 20px; }

/* Card Section */
.card-section { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 20px; padding: 20px; box-shadow: var(--card-shadow); }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.section-header h3 { margin: 0; font-size: 16px; }
.add-btn { padding: 6px 14px; border: 1px solid var(--card-border); border-radius: 20px; background: white; cursor: pointer; font-size: 13px; transition: all 0.2s; }
.add-btn:hover { background: #fff0f6; border-color: #ff9acb; }
.empty-hint { text-align: center; color: var(--text-muted); font-size: 14px; padding: 20px; margin: 0; }

/* Countdown */
.countdown-list { display: flex; flex-direction: column; gap: 12px; }
.countdown-list.scrollable { max-height: 200px; overflow-y: auto; padding-right: 4px; }
.countdown-list.scrollable::-webkit-scrollbar { width: 4px; }
.countdown-list.scrollable::-webkit-scrollbar-thumb { background: #ffcfe3; border-radius: 4px; }
.countdown-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: #fff8fb; border-radius: 12px; position: relative; }
.countdown-item.pinned { background: #fff0f6; border: 1px solid #ffcfe3; }
.countdown-info { flex: 1; min-width: 0; }
.countdown-title { display: block; font-weight: 600; }
.countdown-date { font-size: 12px; color: var(--text-muted); }
.countdown-time { display: flex; align-items: baseline; gap: 2px; flex-shrink: 0; }
.time-num { font-size: 18px; font-weight: 700; color: #c21b68; min-width: 20px; text-align: right; }
.time-unit { font-size: 11px; color: var(--text-muted); margin-right: 6px; }
.time-passed { color: #c21b68; font-weight: 600; }
.pin-icon { margin-right: 4px; }

/* Wish */
.wish-list { display: flex; flex-direction: column; gap: 10px; }
.wish-list.scrollable { max-height: 200px; overflow-y: auto; padding-right: 4px; }
.wish-list.scrollable::-webkit-scrollbar { width: 4px; }
.wish-list.scrollable::-webkit-scrollbar-thumb { background: #ffcfe3; border-radius: 4px; }
.wish-item { display: flex; align-items: center; padding: 12px; background: #fff8fb; border-radius: 12px; position: relative; }
.wish-item.pinned { background: #fff0f6; border: 1px solid #ffcfe3; }
.wish-item.completed { opacity: 0.6; }
.wish-item.completed .wish-title { text-decoration: line-through; }
.wish-checkbox { display: flex; align-items: center; gap: 10px; flex: 1; cursor: pointer; min-width: 0; }
.wish-checkbox input[type="checkbox"] { width: 18px; height: 18px; accent-color: #ff9acb; flex-shrink: 0; }
.wish-title { font-size: 14px; }

/* Editable & Actions */
.editable { cursor: pointer; transition: color 0.2s; }
.editable:hover { color: #c21b68; }
.edit-input { padding: 4px 8px; border: 1px solid #ff9acb; border-radius: 6px; background: white; font-size: 14px; font-weight: 600; width: 100%; }
.edit-input.date-input { width: auto; font-size: 12px; font-weight: 400; margin-top: 4px; }
.item-actions { display: flex; gap: 4px; opacity: 0; transition: opacity 0.2s; }
.countdown-item:hover .item-actions, .wish-item:hover .item-actions { opacity: 1; }
.action-btn { width: 24px; height: 24px; border: none; background: transparent; cursor: pointer; font-size: 14px; border-radius: 4px; transition: background 0.2s; }
.action-btn:hover { background: rgba(0,0,0,0.05); }
.delete-btn { color: #999; }
.delete-btn:hover { color: #e74c3c; }

/* Map */
.map-section { flex: 1; display: flex; flex-direction: column; }
.map-placeholder { flex: 1; min-height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #fff8fb; border-radius: 12px; color: var(--text-muted); }
.placeholder-icon { font-size: 48px; margin-bottom: 12px; }

/* Distance Card */
.distance-card { 
  background: linear-gradient(135deg, #fff8fb 0%, #fff0f6 100%); 
  border-radius: 16px; 
  padding: 16px; 
  margin-bottom: 12px;
}
.distance-header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.distance-icon { font-size: 20px; }
.distance-title { font-size: 15px; font-weight: 600; color: var(--text-main); }
.location-display { display: flex; align-items: center; gap: 12px; }
.location-item { display: flex; align-items: center; gap: 10px; flex: 1; }
.location-avatar { 
  width: 40px; height: 40px; border-radius: 50%; 
  background: white; 
  display: flex; align-items: center; justify-content: center; 
  font-size: 18px; 
  border: 2px solid #ffcfe3;
  background-size: cover; background-position: center;
  flex-shrink: 0;
}
.location-info { display: flex; flex-direction: column; min-width: 0; }
.location-name { font-size: 13px; font-weight: 600; color: var(--text-main); }
.location-addr { font-size: 11px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.distance-line { 
  display: flex; align-items: center; gap: 8px; 
  flex-shrink: 0; padding: 0 8px;
}
.line { width: 20px; height: 2px; background: linear-gradient(90deg, #ffcfe3, #ff9acb); border-radius: 1px; }
.distance-badge { 
  background: linear-gradient(135deg, #ff9acb, #ff6b9d); 
  color: white; 
  padding: 4px 10px; 
  border-radius: 12px; 
  font-size: 12px; 
  font-weight: 600;
  white-space: nowrap;
}
.distance-text { 
  margin: 14px 0 0; 
  text-align: center; 
  font-size: 13px; 
  color: #c21b68; 
}
.distance-text strong { font-size: 20px; font-weight: 700; }

.map-container { flex: 1; min-height: 220px; border-radius: 12px; overflow: hidden; position: relative; background: #f5f5f5; }
.map-loading, .map-error { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.9); }
.map-error { color: #e74c3c; font-size: 14px; }
.spinner { width: 32px; height: 32px; border: 3px solid var(--card-border); border-top-color: #ff9acb; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Game Section - Dice */
.game-section { flex: 1; }
.dice-game { 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  padding: 20px;
  background: linear-gradient(135deg, #fff8fb 0%, #fff0f6 100%);
  border-radius: 12px;
}
.dice-players { display: flex; align-items: center; gap: 24px; margin-bottom: 16px; }
.dice-player { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.player-name { font-size: 14px; font-weight: 600; color: var(--text-main); }
.dice { font-size: 56px; line-height: 1; transition: transform 0.1s; }
.dice.rolling { animation: shake 0.1s infinite; }
@keyframes shake { 
  0%, 100% { transform: rotate(-10deg); } 
  50% { transform: rotate(10deg); } 
}
.dice-num { font-size: 14px; color: #c21b68; font-weight: 600; }
.vs { font-size: 20px; font-weight: 800; color: #ff9acb; }
.dice-result { margin: 0 0 12px; font-size: 16px; font-weight: 600; color: #c21b68; animation: pop 0.3s ease; }
@keyframes pop { 0% { transform: scale(0.8); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
.roll-btn { 
  padding: 12px 28px; 
  border: none; 
  border-radius: 25px; 
  background: linear-gradient(135deg, #ff9acb, #ff6b9d); 
  color: white; 
  font-size: 15px; 
  font-weight: 600; 
  cursor: pointer; 
  transition: all 0.2s;
  box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3);
}
.roll-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 107, 157, 0.4); }
.roll-btn:disabled { opacity: 0.7; cursor: not-allowed; }

/* Edit */
.edit-section { padding: 0 20px 20px; text-align: center; }
.edit-btn { padding: 12px 24px; border: 1px solid var(--card-border); border-radius: 12px; background: white; cursor: pointer; font-weight: 500; transition: all 0.2s; }
.edit-btn:hover { background: #fff0f6; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
.modal { background: white; border-radius: 20px; padding: 24px; width: 100%; max-width: 500px; max-height: 90vh; overflow-y: auto; }
.small-modal { max-width: 380px; }
.modal h3 { margin: 0 0 20px; font-size: 18px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field.full { grid-column: span 2; }
.field span { font-size: 13px; color: var(--text-muted); }
.field input { padding: 10px 12px; border: 1px solid var(--card-border); border-radius: 10px; background: #fff8fb; }
.checkbox-field { display: flex; align-items: center; gap: 8px; margin: 12px 0; }
.checkbox-field input { width: 16px; height: 16px; }

/* Avatar Upload */
.avatar-upload-group { grid-column: span 2; display: flex; justify-content: center; gap: 32px; margin-bottom: 8px; }
.avatar-upload { display: flex; flex-direction: column; align-items: center; gap: 8px; cursor: pointer; }
.avatar-preview { width: 72px; height: 72px; border-radius: 50%; background: #fff0f6; display: flex; align-items: center; justify-content: center; font-size: 24px; border: 2px dashed var(--card-border); background-size: cover; background-position: center; transition: all 0.2s; }
.avatar-upload:hover .avatar-preview { border-color: #ff9acb; }
.avatar-upload span { font-size: 12px; color: var(--text-muted); }

.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px; }
.btn { padding: 10px 20px; border: 1px solid var(--card-border); border-radius: 10px; cursor: pointer; font-weight: 600; transition: all 0.2s; }
.btn.ghost { background: white; }
.btn.primary { background: var(--accent); color: var(--btn-text); border-color: transparent; }
.btn:hover { transform: translateY(-1px); }

@media (max-width: 900px) {
  .main-content { grid-template-columns: 1fr; }
}

@media (max-width: 600px) {
  .quick-grid { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .field.full { grid-column: span 1; }
  .avatar-upload-group { grid-column: span 1; }
}
</style>
