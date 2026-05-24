<template>
    <el-dialog
        v-model="dialogVisible"
        title="预约看房"
        width="480px"
        class="reserve-dialog"
        @closed="handleClosed"
    >
        <div class="reserve-form">
            <div class="form-house-info" v-if="houseInfo">
                <div class="house-name">{{ houseInfo.title }}</div>
                <div class="house-meta-row">
                    <span class="meta-tag">{{ houseInfo.price }}元/月</span>
                    <span class="meta-tag">{{ houseInfo.room || '' }}</span>
                    <span class="meta-tag">{{ houseInfo.area ? `${houseInfo.area}㎡` : '' }}</span>
                </div>
            </div>
            <el-form label-position="top" class="reserve-form-inner">
                <el-form-item label="预约日期" required>
                    <el-date-picker
                        v-model="form.appointment_date"
                        type="date"
                        placeholder="请选择预约日期"
                        style="width: 100%"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                        :disabled-date="disabledDate"
                    />
                </el-form-item>
                <el-form-item label="预约时间" required>
                    <el-time-picker
                        v-model="form.appointment_time"
                        placeholder="请选择预约时间"
                        style="width: 100%"
                        format="HH:mm"
                        value-format="HH:mm"
                    />
                </el-form-item>
                <el-form-item label="备注">
                    <el-input
                        v-model="form.remark"
                        type="textarea"
                        placeholder="请输入备注信息（可选），如您的特殊需求等"
                        :rows="3"
                        maxlength="200"
                        show-word-limit
                    />
                </el-form-item>
            </el-form>
        </div>
        <template #footer>
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" :loading="loading" @click="handleSubmit">提交预约</el-button>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { createAppointment } from '@/api/appointment.js';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    houseInfo: {
        type: Object,
        default: null
    }
});

const emit = defineEmits(['update:visible', 'success']);

const dialogVisible = ref(false);
const loading = ref(false);
const form = ref({
    appointment_date: '',
    appointment_time: '',
    remark: ''
});

watch(() => props.visible, (val) => {
    dialogVisible.value = val;
    if (val) {
        resetForm();
    }
});

watch(dialogVisible, (val) => {
    emit('update:visible', val);
});

const resetForm = () => {
    form.value = {
        appointment_date: '',
        appointment_time: '',
        remark: ''
    };
};

const handleClosed = () => {
    resetForm();
};

// 禁用今天之前的日期
const disabledDate = (time) => {
    return time.getTime() < Date.now() - 8.64e7;
};

const handleSubmit = async () => {
    if (!form.value.appointment_date) {
        ElMessage.warning('请选择预约日期');
        return;
    }
    if (!form.value.appointment_time) {
        ElMessage.warning('请选择预约时间');
        return;
    }
    if (!props.houseInfo?.id) {
        ElMessage.error('房源信息无效');
        return;
    }

    loading.value = true;
    try {
        const res = await createAppointment({
            house_id: props.houseInfo.id,
            appointment_time: `${form.value.appointment_date} ${form.value.appointment_time}`,
            remark: form.value.remark || ''
        });
        if (res.code === 0) {
            ElMessage.success('预约成功！请等待房东确认');
            dialogVisible.value = false;
            emit('success');
        } else {
            ElMessage.error(res.message || '预约失败，请重试');
        }
    } catch (error) {
        console.error('预约失败:', error);
        ElMessage.error('预约失败，请重试');
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.reserve-form {
    padding: 0 4px;
}

.form-house-info {
    padding: 12px 16px;
    background: #f8fafc;
    border-radius: 8px;
    margin-bottom: 20px;
}

.house-name {
    font-size: 15px;
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
}

.house-meta-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.meta-tag {
    padding: 2px 8px;
    background: #e8f4fd;
    color: #006cd8;
    border-radius: 4px;
    font-size: 12px;
}

.reserve-form-inner :deep(.el-form-item__label) {
    font-weight: 500;
    color: #374151;
}
</style>
