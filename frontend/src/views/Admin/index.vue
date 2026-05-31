<template>
  <div class="admin-container">
    <div class="admin-sidebar">
      <div class="sidebar-header">
        <h2 class="sidebar-title">管理后台</h2>
      </div>
      <div class="menu-list">
        <div 
          v-for="item in menuItems" 
          :key="item.key"
          class="menu-item"
          :class="{ active: activeMenu === item.key }"
          @click="handleMenuChange(item.key)"
        >
          <i :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </div>
      </div>
      <div class="sidebar-footer">
        <div class="logout-btn" @click="handleLogout">
          <i class="fa-solid fa-sign-out"></i>
          <span>退出登录</span>
        </div>
      </div>
    </div>

    <div class="admin-content">
      <div class="content-header">
        <h1>{{ currentMenuLabel }}</h1>
        <div class="header-actions">
        </div>
      </div>

      <!-- 用户管理 -->
      <template v-if="activeMenu === 'users'">
        <div class="content-card">
          <el-table :data="users" border stripe v-loading="usersLoading" fit>
            <el-table-column prop="id" label="ID" width="70" align="center" fixed></el-table-column>
            <el-table-column prop="username" label="用户名" min-width="120" show-overflow-tooltip></el-table-column>
            <el-table-column prop="real_name" label="真实姓名" min-width="100" show-overflow-tooltip></el-table-column>
            <el-table-column prop="phone" label="手机号" min-width="130" show-overflow-tooltip></el-table-column>
            <el-table-column prop="email" label="邮箱" min-width="120" show-overflow-tooltip></el-table-column>
            <el-table-column prop="role" label="角色" width="90" align="center">
              <template #default="scope">
                <span :class="`role-badge ${scope.row.role}`">{{ getRoleLabel(scope.row.role) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="scope">
                <span :class="`status-badge ${scope.row.status}`">{{ scope.row.status === 'active' ? '正常' : '禁用' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="175"></el-table-column>
            <el-table-column label="操作" width="160" align="center" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="viewUser(scope.row)">查看</el-button>
                <el-button size="small" :type="scope.row.status === 'active' ? 'danger' : 'success'" @click="toggleUserStatus(scope.row)">
                  {{ scope.row.status === 'active' ? '禁用' : '启用' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <Pagination 
            :page-num="pagination.page"
            :page-size="pagination.pageSize"
            :total="pagination.total"
            @change="handleCurrentChange"
          ></Pagination>
        </div>
      </template>

      <!-- 房源管理 -->
      <template v-if="activeMenu === 'houses'">
        <div class="content-card">
          <el-table :data="houses" border stripe v-loading="housesLoading" fit>
            <el-table-column prop="id" label="ID" width="70" align="center" fixed></el-table-column>
            <el-table-column prop="title" label="标题" min-width="140" show-overflow-tooltip></el-table-column>
            <el-table-column prop="region" label="区域" min-width="100" show-overflow-tooltip></el-table-column>
            <el-table-column prop="house_type" label="户型" min-width="100" show-overflow-tooltip></el-table-column>
            <el-table-column prop="area" label="面积" width="100" align="center">
              <template #default="scope">{{ scope.row.area }}㎡</template>
            </el-table-column>
            <el-table-column prop="rent" label="租金" width="130">
              <template #default="scope">¥{{ scope.row.rent }}/月</template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="scope">
                <span :class="`status-badge ${scope.row.status}`">{{ getHouseStatusLabel(scope.row.status) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="175"></el-table-column>
            <el-table-column label="操作" width="100" align="center" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="viewHouse(scope.row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
          <Pagination 
            :page-num="housePagination.page"
            :page-size="housePagination.pageSize"
            :total="housePagination.total"
            @change="handleHouseCurrentChange"
          ></Pagination>
        </div>
      </template>

      <!-- 投诉管理 -->
      <template v-if="activeMenu === 'complaints'">
        <div class="content-card">
          <el-table :data="complaints" border stripe v-loading="complaintsLoading" fit>
            <el-table-column prop="id" label="ID" width="70" align="center" fixed></el-table-column>
            <el-table-column prop="description" label="投诉内容" min-width="250" show-overflow-tooltip></el-table-column>
            <el-table-column prop="tenant_id" label="投诉人ID" width="100" align="center"></el-table-column>
            <el-table-column prop="contract_id" label="合同ID" width="100" align="center"></el-table-column>
            <el-table-column prop="status" label="状态" width="90" align="center">
              <template #default="scope">
                <span :class="`status-badge ${scope.row.status}`">{{ getComplaintStatusLabel(scope.row.status) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="175"></el-table-column>
            <el-table-column label="操作" width="230" align="center" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="viewComplaint(scope.row)">查看</el-button>
                <el-button 
                  v-if="scope.row.status === 'pending'" 
                  size="small" type="primary" 
                  @click="handleProcessComplaint(scope.row)"
                >处理</el-button>
                <el-button 
                  v-if="scope.row.status === 'processing'" 
                  size="small" type="success" 
                  @click="handleResolveComplaint(scope.row)"
                >解决</el-button>
                <el-button 
                  v-if="scope.row.status === 'pending'" 
                  size="small" type="danger" 
                  @click="handleRejectComplaint(scope.row)"
                >拒绝</el-button>
              </template>
            </el-table-column>
          </el-table>
          <Pagination 
            :page-num="complaintPagination.page"
            :page-size="complaintPagination.pageSize"
            :total="complaintPagination.total"
            @change="handleComplaintCurrentChange"
          ></Pagination>
        </div>
      </template>

      <!-- 报修管理 -->
      <template v-if="activeMenu === 'repairs'">
        <div class="content-card">
          <el-table :data="repairs" border stripe v-loading="repairsLoading" fit>
            <el-table-column prop="id" label="ID" width="70" align="center" fixed></el-table-column>
            <el-table-column prop="title" label="报修标题" min-width="200" show-overflow-tooltip></el-table-column>
            <el-table-column prop="applicant_name" label="申请人" min-width="100" show-overflow-tooltip></el-table-column>
            <el-table-column prop="category" label="分类" width="100" align="center"></el-table-column>
            <el-table-column prop="status" label="状态" width="90" align="center">
              <template #default="scope">
                <span :class="`status-badge ${scope.row.status}`">{{ getRepairStatusLabel(scope.row.status) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="175"></el-table-column>
            <el-table-column label="操作" width="230" align="center" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="viewRepair(scope.row)">查看</el-button>
                <el-button 
                  v-if="scope.row.status === 'pending'" 
                  size="small" type="primary" 
                  @click="handleProcessRepair(scope.row)"
                >处理</el-button>
                <el-button 
                  v-if="scope.row.status === 'processing'" 
                  size="small" type="success" 
                  @click="handleCompleteRepair(scope.row)"
                >完成</el-button>
                <el-button 
                  v-if="scope.row.status === 'pending'" 
                  size="small" type="danger" 
                  @click="handleRejectRepair(scope.row)"
                >拒绝</el-button>
              </template>
            </el-table-column>
          </el-table>
          <Pagination 
            :page-num="repairPagination.page"
            :page-size="repairPagination.pageSize"
            :total="repairPagination.total"
            @change="handleRepairCurrentChange"
          ></Pagination>
        </div>
      </template>

      <!-- 合同管理 -->
      <template v-if="activeMenu === 'contracts'">
        <div class="content-card">
          <el-table :data="contracts" border stripe v-loading="contractsLoading" fit>
            <el-table-column prop="id" label="ID" width="70" align="center" fixed></el-table-column>
            <el-table-column prop="house_title" label="房源" min-width="200" show-overflow-tooltip></el-table-column>
            <el-table-column prop="tenant_name" label="租客" min-width="100" show-overflow-tooltip></el-table-column>
            <el-table-column prop="landlord_name" label="房东" min-width="100" show-overflow-tooltip></el-table-column>
            <el-table-column prop="monthly_rent" label="租金" width="120" align="center">
              <template #default="scope">¥{{ scope.row.monthly_rent }}/月</template>
            </el-table-column>
            <el-table-column prop="start_date" label="起租日期" width="110"></el-table-column>
            <el-table-column prop="end_date" label="到期日期" width="110"></el-table-column>
            <el-table-column prop="status" label="状态" width="90" align="center">
              <template #default="scope">
                <span :class="`status-badge ${scope.row.status}`">{{ getContractStatusLabel(scope.row.status) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="175"></el-table-column>
            <el-table-column label="操作" width="130" align="center" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="viewContract(scope.row)">查看</el-button>
                <el-button 
                  v-if="scope.row.status === 'active'" 
                  size="small" type="danger" 
                  @click="handleCancelContract(scope.row)"
                >终止</el-button>
              </template>
            </el-table-column>
          </el-table>
          <Pagination 
            :page-num="contractPagination.page"
            :page-size="contractPagination.pageSize"
            :total="contractPagination.total"
            @change="handleContractCurrentChange"
          ></Pagination>
        </div>
      </template>

      <!-- 报表统计 -->
      <template v-if="activeMenu === 'statistics'">
        <div class="content-card">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon bg-blue">
                <i class="fa-solid fa-home"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ (statistics.house_utilization * 100).toFixed(2) }}%</div>
                <div class="stat-label">房源利用率</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon bg-green">
                <i class="fa-solid fa-yen-sign"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">¥{{ statistics.rent_income.toLocaleString() }}</div>
                <div class="stat-label">租金收入</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon bg-orange">
                <i class="fa-solid fa-users"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.active_users }}</div>
                <div class="stat-label">活跃用户</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon bg-red">
                <i class="fa-solid fa-flag"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.complaint_count }}</div>
                <div class="stat-label">待处理投诉</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon bg-purple">
                <i class="fa-solid fa-wrench"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.repair_count }}</div>
                <div class="stat-label">待处理报修</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="charts-grid">
          <div class="chart-card">
            <div ref="incomeChartRef" class="chart-container"></div>
          </div>
          <div class="chart-card">
            <div ref="utilizationChartRef" class="chart-container"></div>
          </div>
          <div class="chart-card wide">
            <div ref="complaintRepairChartRef" class="chart-container"></div>
          </div>
        </div>
      </template>

      <!-- 新闻管理 -->
      <template v-if="activeMenu === 'news'">
        <div class="content-card">
          <div style="margin-bottom: 20px;">
            <el-button type="primary" @click="editNewsId = null; newsForm.title = ''; newsForm.content = ''; newsForm.status = 'draft'; showNewsModal = true">
              <i class="fa-solid fa-plus"></i>
              添加新闻
            </el-button>
          </div>
          <el-table :data="news" border stripe v-loading="newsLoading" fit>
            <el-table-column prop="id" label="ID" width="70" align="center" fixed></el-table-column>
            <el-table-column prop="title" label="标题" min-width="300" show-overflow-tooltip></el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="scope">
                <span :class="['news-status-tag', scope.row.status === 'published' ? 'published' : 'draft']">
                  {{ scope.row.status === 'published' ? '已发布' : '草稿' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="175"></el-table-column>
            <el-table-column label="操作" width="180" align="center" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="viewNews(scope.row)">查看</el-button>
                <el-button size="small" type="primary" @click="editNews(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteNews(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <Pagination 
            :page-num="newsPagination.page"
            :page-size="newsPagination.pageSize"
            :total="newsPagination.total"
            @change="handleNewsCurrentChange"
          ></Pagination>
        </div>
      </template>

      <!-- 操作日志 -->
      <template v-if="activeMenu === 'logs'">
        <div class="content-card">
          <el-table :data="logs" border stripe v-loading="logsLoading" fit>
            <el-table-column prop="id" label="ID" width="70" align="center" fixed></el-table-column>
            <el-table-column prop="user_id" label="操作用户" min-width="100" align="center"></el-table-column>
            <el-table-column label="模块" width="90" align="center">
              <template #default="scope">
                <span :class="`log-module-tag ${scope.row.module}`">{{ getModuleLabel(scope.row.module) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center">
              <template #default="scope">
                <span class="log-action-text">{{ getActionLabel(scope.row.action) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="record_id" label="记录ID" min-width="90" align="center"></el-table-column>
            <el-table-column label="前状态" min-width="100" align="center">
              <template #default="scope">
                <span v-if="scope.row.before_status" class="log-status-tag">{{ getStatusCN(scope.row.before_status) }}</span>
                <span v-else style="color: #ccc">-</span>
              </template>
            </el-table-column>
            <el-table-column label="后状态" min-width="100" align="center">
              <template #default="scope">
                <span v-if="scope.row.after_status" class="log-status-tag">{{ getStatusCN(scope.row.after_status) }}</span>
                <span v-else style="color: #ccc">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="操作时间" width="175" fixed="right"></el-table-column>
          </el-table>
          <Pagination 
            :page-num="logPagination.page"
            :page-size="logPagination.pageSize"
            :total="logPagination.total"
            @change="handleLogCurrentChange"
          ></Pagination>
        </div>
      </template>
    </div>

    <!-- 用户详情弹窗 -->
    <el-dialog title="用户详情" v-model="showUserDetail" width="600px">
      <div v-if="selectedUser" class="detail-content">
        <div class="detail-row">
          <span class="detail-label">ID</span>
          <span class="detail-value">{{ selectedUser.id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">用户名</span>
          <span class="detail-value">{{ selectedUser.username }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">真实姓名</span>
          <span class="detail-value">{{ selectedUser.real_name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">手机号</span>
          <span class="detail-value">{{ selectedUser.phone }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">邮箱</span>
          <span class="detail-value">{{ selectedUser.email }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">角色</span>
          <span :class="`role-badge ${selectedUser.role}`">{{ getRoleLabel(selectedUser.role) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">状态</span>
          <span :class="`status-badge ${selectedUser.status}`">{{ selectedUser.status === 'active' ? '正常' : '禁用' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">创建时间</span>
          <span class="detail-value">{{ selectedUser.created_at }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">更新时间</span>
          <span class="detail-value">{{ selectedUser.updated_at }}</span>
        </div>
      </div>
    </el-dialog>

    <!-- 房源详情弹窗 -->
    <el-dialog title="房源详情" v-model="showHouseDetail" width="700px">
      <div v-if="selectedHouse" class="detail-content">
        <div class="detail-row">
          <span class="detail-label">ID</span>
          <span class="detail-value">{{ selectedHouse.id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">房源名称</span>
          <span class="detail-value">{{ selectedHouse.title }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">地址</span>
          <span class="detail-value">{{ selectedHouse.address }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">区域</span>
          <span class="detail-value">{{ selectedHouse.region }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">小区</span>
          <span class="detail-value">{{ selectedHouse.community }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">户型</span>
          <span class="detail-value">{{ selectedHouse.house_type }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">面积</span>
          <span class="detail-value">{{ selectedHouse.area }} ㎡</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">租金</span>
          <span class="detail-value">¥{{ selectedHouse.rent }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">押金</span>
          <span class="detail-value">¥{{ selectedHouse.deposit }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">装修</span>
          <span class="detail-value">{{ selectedHouse.decoration }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">楼层</span>
          <span class="detail-value">{{ selectedHouse.floor }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">朝向</span>
          <span class="detail-value">{{ selectedHouse.orientation }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">状态</span>
          <span :class="`status-badge ${selectedHouse.status}`">{{ getHouseStatusLabel(selectedHouse.status) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">描述</span>
          <span class="detail-value">{{ selectedHouse.description }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">创建时间</span>
          <span class="detail-value">{{ selectedHouse.created_at }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">更新时间</span>
          <span class="detail-value">{{ selectedHouse.updated_at }}</span>
        </div>
      </div>
    </el-dialog>

    <!-- 投诉详情弹窗 -->
    <el-dialog title="投诉详情" v-model="showComplaintDetail" width="600px">
      <div v-if="selectedComplaint" class="detail-content">
        <div class="detail-row">
          <span class="detail-label">ID</span>
          <span class="detail-value">{{ selectedComplaint.id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">描述</span>
          <span class="detail-value">{{ selectedComplaint.description }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">状态</span>
          <span :class="`status-badge ${selectedComplaint.status}`">{{ getComplaintStatusLabel(selectedComplaint.status) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">合同ID</span>
          <span class="detail-value">{{ selectedComplaint.contract_id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">处理时间</span>
          <span class="detail-value">{{ selectedComplaint.processed_at || '无' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">解决时间</span>
          <span class="detail-value">{{ selectedComplaint.resolved_at || '无' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">创建时间</span>
          <span class="detail-value">{{ selectedComplaint.created_at }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">更新时间</span>
          <span class="detail-value">{{ selectedComplaint.updated_at }}</span>
        </div>
      </div>
    </el-dialog>

    <!-- 报修详情弹窗 -->
    <el-dialog title="报修详情" v-model="showRepairDetail" width="600px">
      <div v-if="selectedRepair" class="detail-content">
        <div class="detail-row">
          <span class="detail-label">ID</span>
          <span class="detail-value">{{ selectedRepair.id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">描述</span>
          <span class="detail-value">{{ selectedRepair.description }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">状态</span>
          <span :class="`status-badge ${selectedRepair.status}`">{{ getRepairStatusLabel(selectedRepair.status) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">合同ID</span>
          <span class="detail-value">{{ selectedRepair.contract_id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">处理时间</span>
          <span class="detail-value">{{ selectedRepair.processed_at || '无' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">完成时间</span>
          <span class="detail-value">{{ selectedRepair.completed_at || '无' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">创建时间</span>
          <span class="detail-value">{{ selectedRepair.created_at }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">更新时间</span>
          <span class="detail-value">{{ selectedRepair.updated_at }}</span>
        </div>
      </div>
    </el-dialog>

    <!-- 合同详情弹窗 -->
    <el-dialog title="合同详情" v-model="showContractDetail" width="700px">
      <div v-if="selectedContract" class="detail-content">
        <div class="detail-row">
          <span class="detail-label">ID</span>
          <span class="detail-value">{{ selectedContract.id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">状态</span>
          <span :class="`status-badge ${selectedContract.status}`">{{ getContractStatusLabel(selectedContract.status) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">房源</span>
          <span class="detail-value">{{ selectedContract.house?.title || selectedContract.id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">开始日期</span>
          <span class="detail-value">{{ selectedContract.start_date }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">结束日期</span>
          <span class="detail-value">{{ selectedContract.end_date }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">月租金</span>
          <span class="detail-value">¥{{ selectedContract.monthly_rent }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">押金</span>
          <span class="detail-value">¥{{ selectedContract.deposit }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">备注</span>
          <span class="detail-value">{{ selectedContract.remark || '无' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">创建时间</span>
          <span class="detail-value">{{ selectedContract.created_at }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">更新时间</span>
          <span class="detail-value">{{ selectedContract.updated_at }}</span>
        </div>
      </div>
    </el-dialog>

    <!-- 新闻详情弹窗 -->
    <el-dialog title="新闻详情" v-model="showNewsDetail" width="700px">
      <div v-if="selectedNews" class="detail-content">
        <div class="detail-row">
          <span class="detail-label">ID</span>
          <span class="detail-value">{{ selectedNews.id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">标题</span>
          <span class="detail-value">{{ selectedNews.title }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">内容</span>
          <span class="detail-value" style="white-space: pre-wrap;">{{ selectedNews.content }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">状态</span>
          <span :class="`status-badge ${selectedNews.status}`">{{ selectedNews.status === 'published' ? '已发布' : '草稿' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">创建时间</span>
          <span class="detail-value">{{ selectedNews.created_at }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">更新时间</span>
          <span class="detail-value">{{ selectedNews.updated_at }}</span>
        </div>
      </div>
    </el-dialog>

    <!-- 添加/编辑新闻弹窗 -->
    <el-dialog :title="editNewsId ? '编辑新闻' : '添加新闻'" v-model="showNewsModal" width="700px">
      <el-form label-width="100px">
        <el-form-item label="标题">
          <el-input v-model="newsForm.title" placeholder="请输入新闻标题"></el-input>
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="newsForm.content" type="textarea" :rows="8" placeholder="请输入新闻内容"></el-input>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="newsForm.status">
            <el-option label="草稿" value="draft"></el-option>
            <el-option label="已发布" value="published"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showNewsModal = false">取消</el-button>
        <el-button type="primary" @click="saveNews">保存</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { useUserStore } from '@/stores/user.js'
import Pagination from '@/components/Pagination.vue'
import {
  listUsers, getUserDetail, updateUserStatus,
  listHouses, getHouseDetail,
  listComplaints, getComplaintDetail, processComplaint, resolveComplaint, rejectComplaint,
  listRepairs, getRepairDetail, processRepair, completeRepair, rejectRepair,
  listContracts, getContractDetail, updateContractStatus,
  listLogs
} from '@/api/admin.js'
import {
  getHouseUtilization,
  getRentIncome,
  getActiveUsers,
  getComplaintRepairCount
} from '@/api/statistics.js'
import {
  listNews, getNewsDetail, createNews, updateNews, deleteNews as apiDeleteNews
} from '@/api/news.js'

const userStore = useUserStore()
const activeMenu = ref('users')

const menuItems = [
  { key: 'users', label: '用户管理', icon: 'fa-solid fa-users' },
  { key: 'houses', label: '房源监管', icon: 'fa-solid fa-home' },
  { key: 'complaints', label: '投诉处理', icon: 'fa-solid fa-flag' },
  { key: 'statistics', label: '报表统计', icon: 'fa-solid fa-bar-chart' },
  { key: 'logs', label: '系统监控', icon: 'fa-solid fa-shield' },
  { key: 'news', label: '新闻管理', icon: 'fa-solid fa-newspaper' }
]

const currentMenuLabel = computed(() => {
  const item = menuItems.find(m => m.key === activeMenu.value)
  return item ? item.label : ''
})

// 用户管理
const users = ref([])
const usersLoading = ref(false)
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const showUserDetail = ref(false)
const selectedUser = ref(null)
const showHouseDetail = ref(false)
const selectedHouse = ref(null)
const showComplaintDetail = ref(false)
const selectedComplaint = ref(null)
const showRepairDetail = ref(false)
const selectedRepair = ref(null)
const showContractDetail = ref(false)
const selectedContract = ref(null)

// 房源管理
const houses = ref([])
const housesLoading = ref(false)
const housePagination = reactive({ page: 1, pageSize: 10, total: 0 })

// 投诉管理
const complaints = ref([])
const complaintsLoading = ref(false)
const complaintPagination = reactive({ page: 1, pageSize: 10, total: 0 })

// 报修管理
const repairs = ref([])
const repairsLoading = ref(false)
const repairPagination = reactive({ page: 1, pageSize: 10, total: 0 })

// 合同管理
const contracts = ref([])
const contractsLoading = ref(false)
const contractPagination = reactive({ page: 1, pageSize: 10, total: 0 })

// 操作日志
const logs = ref([])
const logsLoading = ref(false)
const logPagination = reactive({ page: 1, pageSize: 10, total: 0 })

// 新闻管理
const news = ref([])
const newsLoading = ref(false)
const newsPagination = reactive({ page: 1, pageSize: 10, total: 0 })

// 报表统计
const statistics = ref({
  house_utilization: 0,
  rent_income: 0,
  active_users: 0,
  complaint_count: 0,
  repair_count: 0,
  monthly_income: []
})

const incomeChartRef = ref(null)
const utilizationChartRef = ref(null)
const complaintRepairChartRef = ref(null)

let chartInstances = {
  income: null,
  utilization: null,
  complaintRepair: null
}

let resizeBound = false

// 新闻管理
const showNewsModal = ref(false)
const editNewsId = ref(null)
const showNewsDetail = ref(false)
const selectedNews = ref(null)
const newsForm = reactive({
  title: '',
  content: '',
  status: 'draft'
})

const getRoleLabel = (role) => {
  const map = { tenant: '租客', landlord: '房东', admin: '管理员' }
  return map[role] || role
}

const getHouseStatusLabel = (status) => {
  const map = { draft: '草稿', listed: '已上架', offline: '已下架' }
  return map[status] || status
}

const getComplaintStatusLabel = (status) => {
  const map = { pending: '待处理', processing: '处理中', resolved: '已解决', rejected: '已拒绝', closed: '已关闭' }
  return map[status] || status
}

const getModuleLabel = (module) => {
  const map = { repair: '报修', complaint: '投诉', contract: '合同', bill: '账单', payment: '支付', news: '新闻' }
  return map[module] || module
}

const getActionLabel = (action) => {
  const map = {
    create: '创建',
    update: '更新',
    delete: '删除',
    process: '处理',
    resolve: '解决',
    reject: '拒绝',
    complete: '完成',
    cancel: '取消',
    pay: '支付',
    publish: '发布',
    offline: '下架',
    confirm: '确认',
    terminate: '终止'
  }
  return map[action] || action
}

const getStatusCN = (status) => {
  if (!status) return ''
  const map = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已解决',
    completed: '已完成',
    rejected: '已拒绝',
    closed: '已关闭',
    cancelled: '已取消',
    active: '生效中',
    expired: '已到期',
    draft: '草稿',
    published: '已发布',
    unpaid: '未支付',
    paid: '已支付'
  }
  return map[status] || status
}

const formatLogTime = (dateStr) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now - date
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    
    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

const getRepairStatusLabel = (status) => {
  const map = { pending: '待处理', processing: '处理中', completed: '已完成', rejected: '已拒绝', closed: '已关闭' }
  return map[status] || status
}

const getContractStatusLabel = (status) => {
  const map = { pending: '待签署', active: '生效中', cancelled: '已取消', expired: '已到期' }
  return map[status] || status
}

const loadUsers = async () => {
  usersLoading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    
    const res = await listUsers(params)
    if (res.code === 0 && res.data) {
      users.value = res.data.items || res.data.list || []
      pagination.total = res.data.total || 0
    }
  } catch (e) {
    console.error('加载用户列表失败', e)
    ElMessage.error('加载用户列表失败')
  } finally {
    usersLoading.value = false
  }
}

const loadHouses = async () => {
  housesLoading.value = true
  try {
    const params = {
      page: housePagination.page,
      page_size: housePagination.pageSize
    }
    
    const res = await listHouses(params)
    if (res.code === 0 && res.data) {
      houses.value = res.data.items || res.data.list || []
      housePagination.total = res.data.total || 0
    }
  } catch (e) {
    console.error('加载房源列表失败', e)
    ElMessage.error('加载房源列表失败')
  } finally {
    housesLoading.value = false
  }
}

const loadComplaints = async () => {
  complaintsLoading.value = true
  try {
    const params = {
      page: complaintPagination.page,
      page_size: complaintPagination.pageSize
    }
    
    const res = await listComplaints(params)
    if (res.code === 0 && res.data) {
      complaints.value = res.data.items || res.data.list || []
      complaintPagination.total = res.data.total || 0
    }
  } catch (e) {
    console.error('加载投诉列表失败', e)
    ElMessage.error('加载投诉列表失败')
  } finally {
    complaintsLoading.value = false
  }
}

const loadRepairs = async () => {
  repairsLoading.value = true
  try {
    const params = {
      page: repairPagination.page,
      page_size: repairPagination.pageSize
    }
    
    const res = await listRepairs(params)
    if (res.code === 0 && res.data) {
      repairs.value = res.data.items || res.data.list || []
      repairPagination.total = res.data.total || 0
    }
  } catch (e) {
    console.error('加载报修列表失败', e)
    ElMessage.error('加载报修列表失败')
  } finally {
    repairsLoading.value = false
  }
}

const loadContracts = async () => {
  contractsLoading.value = true
  try {
    const params = {
      page: contractPagination.page,
      page_size: contractPagination.pageSize
    }
    
    const res = await listContracts(params)
    if (res.code === 0 && res.data) {
      contracts.value = res.data.items || res.data.list || []
      contractPagination.total = res.data.total || 0
    }
  } catch (e) {
    console.error('加载合同列表失败', e)
    ElMessage.error('加载合同列表失败')
  } finally {
    contractsLoading.value = false
  }
}

const loadLogs = async () => {
  logsLoading.value = true
  try {
    const params = {
      page: logPagination.page,
      page_size: logPagination.pageSize
    }
    
    const res = await listLogs(params)
    if (res.code === 0 && res.data) {
      logs.value = res.data.items || res.data.list || []
      logPagination.total = res.data.total || 0
    }
  } catch (e) {
    console.error('加载日志列表失败', e)
    ElMessage.error('加载日志列表失败')
  } finally {
    logsLoading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const [utilizationRes, incomeRes, usersRes, countRes] = await Promise.all([
      getHouseUtilization(),
      getRentIncome(),
      getActiveUsers(),
      getComplaintRepairCount()
    ])
    
    if (utilizationRes.code === 0) {
      statistics.value.house_utilization = utilizationRes.data.utilization_rate || 0
    }
    if (incomeRes.code === 0) {
      statistics.value.rent_income = parseFloat(incomeRes.data.total_income) || 0
      statistics.value.monthly_income = incomeRes.data.monthly_income || []
    }
    if (usersRes.code === 0) {
      statistics.value.active_users = usersRes.data.active_user_count || 0
    }
    if (countRes.code === 0) {
      statistics.value.complaint_count = countRes.data.complaint_count || 0
      statistics.value.repair_count = countRes.data.repair_count || 0
    }
    
    await nextTick()
    renderCharts()
  } catch (e) {
    console.error('加载统计数据失败', e)
    ElMessage.error('加载统计数据失败')
  }
}

const renderCharts = () => {
  renderIncomeChart()
  renderUtilizationChart()
  renderComplaintRepairChart()
  
  if (!resizeBound) {
    window.addEventListener('resize', handleResize)
    resizeBound = true
  }
}

const renderIncomeChart = () => {
  const container = incomeChartRef.value
  if (!container) return
  
  if (chartInstances.income) {
    chartInstances.income.dispose()
  }
  
  chartInstances.income = echarts.init(container)
  
  const monthlyIncome = statistics.value.monthly_income || []
  const months = monthlyIncome.map(item => item.month)
  const amounts = monthlyIncome.map(item => item.amount)
  
  const option = {
    title: {
      text: '月度租金收入趋势',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>租金收入: ¥{c}'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: {
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '租金收入',
        type: 'line',
        smooth: true,
        data: amounts,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
              { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
            ]
          }
        },
        lineStyle: {
          color: '#3B82F6',
          width: 3
        },
        itemStyle: {
          color: '#3B82F6'
        },
        symbol: 'circle',
        symbolSize: 8
      }
    ]
  }
  
  chartInstances.income.setOption(option)
}

const renderUtilizationChart = () => {
  const container = utilizationChartRef.value
  if (!container) return
  
  if (chartInstances.utilization) {
    chartInstances.utilization.dispose()
  }
  
  chartInstances.utilization = echarts.init(container)
  
  const utilizationRate = statistics.value.house_utilization * 100
  const unoccupiedRate = 100 - utilizationRate
  
  const option = {
    title: {
      text: '房源利用率',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}% ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: '5%'
    },
    series: [
      {
        name: '房源状态',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        data: [
          { value: utilizationRate.toFixed(1), name: '已占用', itemStyle: { color: '#22c55e' } },
          { value: unoccupiedRate.toFixed(1), name: '空闲', itemStyle: { color: '#f59e0b' } }
        ]
      }
    ]
  }
  
  chartInstances.utilization.setOption(option)
}

const renderComplaintRepairChart = () => {
  const container = complaintRepairChartRef.value
  if (!container) return
  
  if (chartInstances.complaintRepair) {
    chartInstances.complaintRepair.dispose()
  }
  
  chartInstances.complaintRepair = echarts.init(container)
  
  const complaintCount = statistics.value.complaint_count || 0
  const repairCount = statistics.value.repair_count || 0
  
  const option = {
    title: {
      text: '待处理工单统计',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: '{b}<br/>数量: {c}'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['投诉', '报修'],
      axisLabel: {
        fontSize: 14,
        fontWeight: '500'
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      axisLabel: {
        formatter: '{value} 件'
      }
    },
    series: [
      {
        name: '工单数量',
        type: 'bar',
        barWidth: '50%',
        data: [
          { value: complaintCount, itemStyle: { color: '#ef4444', borderRadius: [6, 6, 0, 0] } },
          { value: repairCount, itemStyle: { color: '#8b5cf6', borderRadius: [6, 6, 0, 0] } }
        ]
      }
    ]
  }
  
  chartInstances.complaintRepair.setOption(option)
}

const handleResize = () => {
  Object.values(chartInstances).forEach(chart => {
    if (chart) {
      chart.resize()
    }
  })
}

const disposeCharts = () => {
  Object.keys(chartInstances).forEach(key => {
    if (chartInstances[key]) {
      chartInstances[key].dispose()
      chartInstances[key] = null
    }
  })
  window.removeEventListener('resize', handleResize)
}

const loadNews = async () => {
  newsLoading.value = true
  try {
    const params = {
      page: newsPagination.page,
      page_size: newsPagination.pageSize
    }
    
    const res = await listNews(params)
    if (res.code === 0 && res.data) {
      news.value = res.data.items || res.data.list || []
      newsPagination.total = res.data.total || 0
    }
  } catch (e) {
    console.error('加载新闻列表失败', e)
    ElMessage.error('加载新闻列表失败')
  } finally {
    newsLoading.value = false
  }
}

const viewNews = async (newsItem) => {
  try {
    const res = await getNewsDetail(newsItem.id)
    if (res.code === 0 && res.data) {
      selectedNews.value = res.data
      showNewsDetail.value = true
    }
  } catch (e) {
    console.error('获取新闻详情失败', e)
    ElMessage.error('获取新闻详情失败')
  }
}

const editNews = (newsItem) => {
  editNewsId.value = newsItem.id
  newsForm.title = newsItem.title
  newsForm.content = newsItem.content || ''
  newsForm.status = newsItem.status
  showNewsModal.value = true
}

const saveNews = async () => {
  if (!newsForm.title) {
    ElMessage.warning('请输入新闻标题')
    return
  }
  if (!newsForm.content) {
    ElMessage.warning('请输入新闻内容')
    return
  }
  try {
    const data = {
      title: newsForm.title,
      content: newsForm.content,
      status: newsForm.status
    }
    let res
    if (editNewsId.value) {
      res = await updateNews(editNewsId.value, data)
    } else {
      res = await createNews(data)
    }
    if (res.code === 0) {
      ElMessage.success(editNewsId.value ? '修改成功' : '创建成功')
      showNewsModal.value = false
      editNewsId.value = null
      newsForm.title = ''
      newsForm.content = ''
      newsForm.status = 'draft'
      loadNews()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    console.error('保存新闻失败', e)
    ElMessage.error('保存失败')
  }
}

const deleteNews = async (newsItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除新闻 #${newsItem.id} 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    const res = await apiDeleteNews(newsItem.id)
    if (res.code === 0) {
      ElMessage.success('删除成功')
      loadNews()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除新闻失败', e)
      ElMessage.error('删除新闻失败')
    }
  }
}

const viewUser = async (user) => {
  try {
    const res = await getUserDetail(user.id)
    if (res.code === 0 && res.data) {
      selectedUser.value = res.data
      showUserDetail.value = true
    }
  } catch (e) {
    console.error('获取用户详情失败', e)
    ElMessage.error('获取用户详情失败')
  }
}

const toggleUserStatus = async (user) => {
  try {
    const newStatus = user.status === 'active' ? 'disabled' : 'active'
    await ElMessageBox.confirm(
      `确定要${newStatus === 'active' ? '启用' : '禁用'}用户 #${user.id} 吗？`,
      '确认操作',
      { type: 'warning' }
    )
    
    const res = await updateUserStatus(user.id, newStatus)
    if (res.code === 0) {
      ElMessage.success(`${newStatus === 'active' ? '已启用' : '已禁用'}`)
      loadUsers()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      console.error('操作失败', e)
      ElMessage.error('操作失败')
    }
  }
}

const viewHouse = async (house) => {
  try {
    const res = await getHouseDetail(house.id)
    if (res.code === 0 && res.data) {
      selectedHouse.value = res.data
      showHouseDetail.value = true
    }
  } catch (e) {
    console.error('获取房源详情失败', e)
    ElMessage.error('获取房源详情失败')
  }
}

const viewComplaint = async (complaint) => {
  try {
    const res = await getComplaintDetail(complaint.id)
    if (res.code === 0 && res.data) {
      selectedComplaint.value = res.data
      showComplaintDetail.value = true
    }
  } catch (e) {
    console.error('获取投诉详情失败', e)
    ElMessage.error('获取投诉详情失败')
  }
}

const handleProcessComplaint = async (complaint) => {
  try {
    const res = await processComplaint(complaint.id)
    if (res.code === 0) {
      ElMessage.success('已开始处理')
      loadComplaints()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    console.error('处理投诉失败', e)
    ElMessage.error('处理投诉失败')
  }
}

const handleResolveComplaint = async (complaint) => {
  try {
    const res = await resolveComplaint(complaint.id)
    if (res.code === 0) {
      ElMessage.success('已解决')
      loadComplaints()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    console.error('解决投诉失败', e)
    ElMessage.error('解决投诉失败')
  }
}

const handleRejectComplaint = async (complaint) => {
  try {
    const res = await rejectComplaint(complaint.id)
    if (res.code === 0) {
      ElMessage.success('已拒绝')
      loadComplaints()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    console.error('拒绝投诉失败', e)
    ElMessage.error('拒绝投诉失败')
  }
}

const viewRepair = async (repair) => {
  try {
    const res = await getRepairDetail(repair.id)
    if (res.code === 0 && res.data) {
      selectedRepair.value = res.data
      showRepairDetail.value = true
    }
  } catch (e) {
    console.error('获取报修详情失败', e)
    ElMessage.error('获取报修详情失败')
  }
}

const handleProcessRepair = async (repair) => {
  try {
    const res = await processRepair(repair.id)
    if (res.code === 0) {
      ElMessage.success('已开始处理')
      loadRepairs()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    console.error('处理报修失败', e)
    ElMessage.error('处理报修失败')
  }
}

const handleCompleteRepair = async (repair) => {
  try {
    const res = await completeRepair(repair.id)
    if (res.code === 0) {
      ElMessage.success('已完成')
      loadRepairs()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    console.error('完成报修失败', e)
    ElMessage.error('完成报修失败')
  }
}

const handleRejectRepair = async (repair) => {
  try {
    const res = await rejectRepair(repair.id)
    if (res.code === 0) {
      ElMessage.success('已拒绝')
      loadRepairs()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    console.error('拒绝报修失败', e)
    ElMessage.error('拒绝报修失败')
  }
}

const viewContract = async (contract) => {
  try {
    const res = await getContractDetail(contract.id)
    if (res.code === 0 && res.data) {
      selectedContract.value = res.data
      showContractDetail.value = true
    }
  } catch (e) {
    console.error('获取合同详情失败', e)
    ElMessage.error('获取合同详情失败')
  }
}

const handleCancelContract = async (contract) => {
  try {
    await ElMessageBox.confirm(
      `确定要终止合同 #${contract.id} 吗？`,
      '确认终止',
      { type: 'warning' }
    )
    
    const res = await updateContractStatus(contract.id, 'cancelled')
    if (res.code === 0) {
      ElMessage.success('已终止')
      loadContracts()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      console.error('终止合同失败', e)
      ElMessage.error('终止合同失败')
    }
  }
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadUsers()
}

const handleHouseCurrentChange = (page) => {
  housePagination.page = page
  loadHouses()
}

const handleComplaintCurrentChange = (page) => {
  complaintPagination.page = page
  loadComplaints()
}

const handleRepairCurrentChange = (page) => {
  repairPagination.page = page
  loadRepairs()
}

const handleContractCurrentChange = (page) => {
  contractPagination.page = page
  loadContracts()
}

const handleLogCurrentChange = (page) => {
  logPagination.page = page
  loadLogs()
}

const handleNewsCurrentChange = (page) => {
  newsPagination.page = page
  loadNews()
}

const handleMenuChange = (menu) => {
  activeMenu.value = menu
  switch (menu) {
    case 'users':
      loadUsers()
      break
    case 'houses':
      loadHouses()
      break
    case 'complaints':
      loadComplaints()
      break
    case 'statistics':
      loadStatistics()
      break
    case 'logs':
      loadLogs()
      break
    case 'news':
      loadNews()
      break
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '确认退出',
      { type: 'warning' }
    )
    
    userStore.logout()
    router.push('/')
  } catch (e) {
    if (e !== 'cancel') {
      console.error('退出失败', e)
    }
  }
}

onMounted(() => {
  handleMenuChange('users')
})

watch(activeMenu, (newMenu, oldMenu) => {
  if (oldMenu === 'statistics' && newMenu !== 'statistics') {
    disposeCharts()
  }
})
</script>

<style scoped>
.admin-container {
  display: flex;
  min-height: 100vh;
  background: #f5f5f5;
}

.admin-sidebar {
  width: 220px;
  background: #1f2937;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-bottom: 50px;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #374151;
}

.sidebar-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.menu-list {
  flex: 1;
  padding: 10px 0;
}

.sidebar-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 220px;
  padding: 10px 0;
  border-top: 1px solid #374151;
  background: #1f2937;
}

.logout-btn {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: background 0.2s;
  color: #ef4444;
}

.logout-btn:hover {
  background: #374151;
}

.logout-btn i {
  margin-right: 10px;
  width: 20px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.menu-item:hover {
  background: #374151;
}

.menu-item.active {
  background: #3b82f6;
}

.menu-item i {
  margin-right: 10px;
  width: 20px;
}

.admin-content {
  flex: 1;
  padding: 20px;
  margin-left: 220px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.content-header h1 {
  margin: 0;
  font-size: 24px;
}

.content-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.content-card .el-table {
  width: 100%;
}

.content-card .el-table .el-table__cell {
  padding: 8px 12px !important;
}

.content-card .el-table .el-button + .el-button {
  margin-left: 6px;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.search-input {
  width: 300px;
}

.filter-select {
  width: 140px;
}

.role-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
}

.role-badge.tenant {
  background: #dbeafe;
  color: #2563eb;
}

.role-badge.landlord {
  background: #dcfce7;
  color: #16a34a;
}

.role-badge.admin {
  background: #fef3c7;
  color: #d97706;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
}

.status-badge.active {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #dc2626;
}

.status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.processing {
  background: #dbeafe;
  color: #2563eb;
}

.status-badge.resolved,
.status-badge.completed {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #dc2626;
}

.status-badge.closed {
  background: #f3f4f6;
  color: #6b7280;
}

.status-badge.listed {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge.offline {
  background: #fee2e2;
  color: #dc2626;
}

.status-badge.draft {
  background: #fef3c7;
  color: #d97706;
}

.news-status-tag {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.news-status-tag.published {
  background: #dcfce7;
  color: #16a34a;
}

.news-status-tag.draft {
  background: #fef3c7;
  color: #d97706;
}

.detail-content {
  padding: 10px;
}

.detail-row {
  display: flex;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-label {
  width: 100px;
  color: #666;
  font-weight: 500;
}

.detail-value {
  flex: 1;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.news-title-cell {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.table-actions {
  display: flex;
  gap: 6px;
}

:deep(.el-table) {
  border-radius: 8px;
}

:deep(.el-table .el-table__cell > .cell) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.el-table--border) {
  border-color: #e8e8e8;
}

:deep(.el-table th.el-table__cell) {
  background: #fafafa;
  font-weight: 600;
  color: #262626;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: #f7f9fc;
}

:deep(.el-table__body tr:hover > td) {
  background: #e6f7ff !important;
}

:deep(.el-table__column-resize-proxy) {
  border-left: 2px solid #409eff;
  z-index: 10;
}

:deep(.el-table th.el-table__cell.is-leaf) {
  cursor: col-resize;
}

:deep(.el-table__header-wrapper) {
  user-select: none;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  color: #fff;
  font-size: 24px;
}

.stat-icon.bg-blue {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.stat-icon.bg-green {
  background: linear-gradient(135deg, #22c55e, #15803d);
}

.stat-icon.bg-orange {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.stat-icon.bg-red {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.stat-icon.bg-purple {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
}

.chart-container {
  width: 100%;
  height: 350px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 20px;
}

.chart-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 20px;
}

.chart-card.wide {
  grid-column: span 2;
}

.log-action-text {
  font-size: 13px;
  font-weight: 600;
  color: #3b82f6;
  background: #eff6ff;
  padding: 2px 10px;
  border-radius: 12px;
}

.log-status-tag {
  display: inline-block;
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 12px;
  background: #f3f4f6;
  color: #6b7280;
}

.log-module-tag {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.log-module-tag.repair {
  background: #f3e8ff;
  color: #7c3aed;
}

.log-module-tag.complaint {
  background: #fee2e2;
  color: #dc2626;
}

.log-module-tag.contract {
  background: #dbeafe;
  color: #1d4ed8;
}

.log-module-tag.bill {
  background: #fef3c7;
  color: #d97706;
}

.log-module-tag.payment {
  background: #dcfce7;
  color: #15803d;
}

.log-module-tag.news {
  background: #cffafe;
  color: #0891b2;
}
</style>