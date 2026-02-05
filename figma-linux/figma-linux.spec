%global         __provides_exclude_from ^/opt/%{name}/.*$
%global         __requires_exclude_from ^/opt/%{name}/.*$
%global         app_name Figma-Linux
%global         debug_package %nil

Name:           %(echo %app_name | tr '[:upper:]' '[:lower:]')
Version:        0.11.5
Release:        1%{?dist}
Summary:        %{app_name} is an unofficial Electron-based Figma desktop app for Linux.

License:        GPL-2.0
URL:            https://github.com/%{app_name}/%{name}

Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

Patch0:         config_builder.json_diff.patch

BuildRequires:  electron nodejs nodejs-npm
%ifarch %arm64
BuildRequires:  python3 gcc gcc-c++ make cmake libtool
BuildRequires:  libX11-devel libsecret-devel xz-devel libXScrnSaver-devel
BuildRequires:  alsa-lib-devel libXtst-devel mesa-libgbm-devel
BuildRequires:  libindicator-gtk3-devel libdbusmenu-gtk3-devel
BuildRequires:  libdbusmenu-devel pam-devel glib2-devel libtool-ltdl-devel
%endif

# ExclusiveArch:  x86_64

%description
%summary


%prep
%autosetup -p1 -n ./%{name}-%{version}


%build -p %{_bindir}/bash
%if %{?fedora} >= 44
  mkdir -v ./extra_bin
  ln -sv $(command -v node-22) ./extra_bin/node
  ln -sv $(command -v npm-22) ./extra_bin/npm
  export PATH="$PATH:$(realpath ./extra_bin)"
%endif

# Ensure nodejs does not download an electron executable
export ELECTRON_SKIP_BINARY_DOWNLOAD=1
export ELECTRON_OVERRIDE_DIST_PATH='%{_libdir}/electron'

# Change the node and electron cache dir to
# avoid errors in COPR's cloud environment
export npm_config_cache="$(realpath ./.node_cache)"
# export ELECTRON_CACHE="$(realpath ./.electron_cache)"

# Change where npm stores its
# user and global config
export NPM_CONFIG_USERCONFIG="$(realpath ./user_npmrc)"
export NPM_CONFIG_GLOBALCONFIG="$(realpath ./npmrc)"
touch ./user_npmrc ./npmrc

# Install the dependencies
%ifarch %arm64
env NODE_ENV='dev' npm install --ignore-scripts

NODE_GYP_PATH="$(realpath ./node_modules/.bin/node-gyp)"
pushd ./node_modules/lzma-native
"$NODE_GYP_PATH" rebuild --build-from-source
popd
# keytar does not exist
# "$NODE_GYP_PATH" rebuild --directory ./node_modules/keytar
%else
env NODE_ENV='dev' npm install
%endif

# Generate important build files
export NODE_ENV='production'
npm run build

# Build the application
npm run builder -- \
  "-c.electronDist=$ELECTRON_OVERRIDE_DIST_PATH"


%install
# Setup buildroot
install -d %{buildroot}{/opt/%{name},%{_bindir},%{_datadir}/applications}

sizes=(
  '24x24' '36x36' '48x48' '64x64' '72x72' '96x96'
  '128x128' '192x192' '256x256' '384x384' '512x512'
)
for size in "${sizes[@]}"; do
  install -d "%{buildroot}%{_iconsdir}/hicolor/$size/apps"
done
install -d %{buildroot}%{_iconsdir}/hicolor/scalable/apps

# Reusable constant
BUILD_DIR=./build/installers/linux-unpacked

# Remove unneeded files in the build directory
rm -r "$BUILD_DIR"/{usr,lib,AppRun} "$BUILD_DIR"/*.sh

# Copy the application files to the application directory
cp -a "$BUILD_DIR"/* %{buildroot}/opt/%{name}

# Install the desktop file
install -Dm 0644 ./resources/%{name}.desktop -t %{buildroot}%{_datadir}/applications

# Create a symlink to the application binary
ln -s /opt/%{name}/%{name} %{buildroot}%{_bindir}

# Install application icons
for size in "${sizes[@]}"; do
  install -Dm 0644 "$BUILD_DIR/icons/$size.png" \
    "%{buildroot}%{_iconsdir}/hicolor/$size/apps/%{name}.png"
done
install -Dm 0644 "$BUILD_DIR/icons/scalable.svg" \
  %{buildroot}%{_iconsdir}/hicolor/scalable/apps/%{name}.png

# Remove unneeded files in the application directory
rm -r %{buildroot}/opt/%{name}/icons


%files
/opt/%{name}
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_iconsdir}/hicolor/*/apps/%{name}.png

%changelog
%autochangelog
